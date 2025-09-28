# messaging_app/chats/permissions.py

from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to view, update, and delete messages within it.
    """

    def has_permission(self, request, view):
        # Allow access only if the user is authenticated (global access control)
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant of the conversation.
        # This logic handles both Conversation and Message objects.

        # 1. Determine the Conversation object
        if hasattr(obj, 'participants'):
            # If 'obj' is a Conversation instance
            conversation = obj
        elif hasattr(obj, 'conversation'):
            # If 'obj' is a Message instance (assuming Message model has a 'conversation' foreign key)
            conversation = obj.conversation
        else:
            # The object type is unexpected; deny access
            return False

        # 2. Check if the user is in the conversation's 'participants' field
        # Assuming 'participants' is a ManyToMany field on the Conversation model.
        return conversation.participants.filter(pk=request.user.pk).exists()