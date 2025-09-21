from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'role']
        read_only_fields = ['user_id', 'email']

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    It includes nested user data for the sender.
    """
    sender = UserSerializer(read_only=True)
    # Using CharField to represent the message body
    message_body = serializers.CharField(max_length=2000)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']

    def validate_message_body(self, value):
        """
        Example of custom validation.
        Ensures the message body is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    It includes nested relationships for participants and messages.
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']

    def get_messages(self, obj):
        """
        Returns a list of messages for the conversation.
        """
        messages = obj.messages.all().order_by('sent_at')
        return MessageSerializer(messages, many=True).data

    def validate(self, data):
        """
        Example of object-level validation.
        """
        if 'participants' not in data and self.instance is None:
            # This is a hypothetical check for creating a new conversation
            # with at least one participant.
            raise serializers.ValidationError("New conversations must have participants.")
        return data
