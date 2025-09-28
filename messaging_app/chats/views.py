from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer

from rest_framework import generics
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

from .permissions import IsParticipantOfConversation
from rest_framework import viewsets

from .pagination import MessagePagination # Import custom pagination
from .filters import MessageFilter

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling conversations.
    Provides list, retrieve, create, and other actions.
    """
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Add filter backends to allow searching and filtering
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['participants'] # Allows filtering conversations by participant ID

    def get_queryset(self):
        """
        Filters conversations to only show those the current user is a participant of.
        """
        return self.request.user.conversations.all().order_by('-created_at')

    def perform_create(self, serializer):
        """
        Custom create method to add the current user as a participant.
        """
        # Save the new conversation instance.
        conversation = serializer.save()
        # Add the creating user as a participant.
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'], url_path='send_message')
    def send_message(self, request, pk=None):
        """
        Custom action to send a new message to an existing conversation.
        """
        conversation = self.get_object()
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            # Check if the user is a participant in the conversation
            if self.request.user not in conversation.participants.all():
                return Response(
                    {"detail": "You are not a participant in this conversation."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Create the message and associate it with the sender and conversation.
            message = serializer.save(
                sender=self.request.user,
                conversation=conversation
            )
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling messages.
    Provides a list of messages within a conversation and allows message creation.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Add filter backends
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['conversation', 'sender'] # Allows filtering messages by conversation ID or sender

    def get_queryset(self):
        """
        This view should return a list of all messages
        for the currently authenticated user's conversations.
        """
        user = self.request.user
        conversations = user.conversations.all()
        return Message.objects.filter(conversation__in=conversations).order_by('sent_at')

    def perform_create(self, serializer):
        """
        Custom create method to associate the message with the current user.
        """
        # Ensure the conversation exists and the user is a participant.
        conversation_id = self.request.data.get('conversation')
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError({"detail": "Conversation not found."})

        if self.request.user not in conversation.participants.all():
            raise serializers.ValidationError({"detail": "You are not a participant in this conversation."})

        serializer.save(sender=self.request.user, conversation=conversation)

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsOwnerOrReadOnly] # Apply permission if needed for creation

    def get_queryset(self):
        # Crucial step: Filter the queryset to only include conversations belonging to the current user
        return Conversation.objects.filter(participants=self.request.user)

class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all() # Or use a smaller base set, but the permission ensures security
    serializer_class = MessageSerializer
    permission_classes = [IsOwnerOrReadOnly] # Ensure only the owner can modify/delete

class ConversationViewSet(viewsets.ModelViewSet):
    # Only authenticated users who are participants can access/modify conversations
    permission_classes = [IsParticipantOfConversation]

    # Ensure only the user's conversations are listed (Participant check for list action)
    def get_queryset(self):
        return self.request.user.conversations.all()
        # Assumes a 'conversations' related_name exists on the User model
        # or you use Conversation.objects.filter(participants=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    # Only authenticated users who are participants can access/modify messages
    permission_classes = [IsParticipantOfConversation]

    # You might want to override get_queryset to scope messages to a specific conversation
    # For a general list view:
    def get_queryset(self):
        # Only return messages from conversations the user is a participant of
        user_conversations = self.request.user.conversations.all()
        return Message.objects.filter(conversation__in=user_conversations)


class MessageViewSet(viewsets.ModelViewSet):
    # Ensure permission is still enforced
    permission_classes = [IsParticipantOfConversation]
    # serializer_class = MessageSerializer

    # --- New: Add Pagination and Filtering ---
    pagination_class = MessagePagination
    filterset_class = MessageFilter
    # Required for django-filters
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    # Existing method to scope messages to the user's conversations
    def get_queryset(self):
        # Only return messages from conversations the user is a participant of
        user_conversations = self.request.user.conversations.all()
        return Message.objects.filter(conversation__in=user_conversations).order_by('-timestamp') # Order for time-based display/pagination