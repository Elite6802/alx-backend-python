from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer

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
