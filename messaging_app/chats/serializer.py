from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'role']
        read_only_fields = ['user_id', 'email'] # user_id is set on creation, email is read-only after creation.

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    It includes nested user data for the sender.
    """
    # Nested serializer to include sender details
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    It includes nested relationships for participants and messages.
    """
    # This field handles the many-to-many relationship with users,
    # nesting the UserSerializer for each participant.
    participants = UserSerializer(many=True, read_only=True)

    # This field handles the reverse relationship from Conversation to Message,
    # nesting all messages within the conversation.
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']
