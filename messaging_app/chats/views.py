
from django.shortcuts import render
from rest_framework import viewsets, permissions, status, serializers, generics, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer
from .permissions import IsParticipantOrSender
from .pagination import MessagePagination
from .filters import MessageFilter


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling conversations.
    Provides list, retrieve, create, and other actions.
    """
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOrSender]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['participants']  # Allows filtering conversations by participant ID

    def get_queryset(self):
        """Only show conversations the current user is a participant of."""
        return self.request.user.conversations.all().order_by('-created_at')

    def perform_create(self, serializer):
        """Add the creating user as a participant when a conversation is created."""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'], url_path='send_message')
    def send_message(self, request, pk=None):
        """Custom action to send a new message in a conversation."""
        conversation = self.get_object()
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            if self.request.user not in conversation.participants.all():
                return Response(
                    {"detail": "You are not a participant in this conversation."},
                    status=status.HTTP_403_FORBIDDEN
                )
            message = serializer.save(
                sender=self.request.user,
                conversation=conversation
            )
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling messages.
    Provides list, retrieve, create, update, and delete actions.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOrSender]
    pagination_class = MessagePagination
    filterset_class = MessageFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        """Return only messages from conversations the user participates in."""
        user_conversations = self.request.user.conversations.all()
        return Message.objects.filter(conversation__in=user_conversations).order_by('-sent_at')

    def perform_create(self, serializer):
        """Ensure user is a participant when creating a message."""
        conversation_id = self.request.data.get('conversation')
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError({"detail": "Conversation not found."})

        if self.request.user not in conversation.participants.all():
            raise serializers.ValidationError({"detail": "You are not a participant in this conversation."})

        serializer.save(sender=self.request.user, conversation=conversation)


class ConversationListCreateView(generics.ListCreateAPIView):
    """List and create conversations."""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single message."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOrSender]
