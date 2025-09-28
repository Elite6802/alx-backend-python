from rest_framework import permissions
# Corrects the import name
# from .permissions import IsParticipantOrSender

class IsParticipantOrSender(permissions.BasePermission):
    """
    Custom permission to only allow participants of a Conversation or
    the sender of a Message to interact with the object.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any participant/sender.
        if request.method in permissions.SAFE_METHODS:
            # Check for Conversation object
            if hasattr(obj, 'participants'):
                return request.user in obj.participants.all()

            # Check for Message object
            if hasattr(obj, 'sender'):
                return request.user == obj.sender or request.user in obj.conversation.participants.all()

            return False

        # Write permissions (PUT, DELETE) are generally restricted to the owner/sender.
        # Customize this logic based on your exact business rules (e.g., only sender can delete a message)
        if hasattr(obj, 'sender'):
            return request.user == obj.sender

        # For Conversation, only a participant may update/leave it, but often
        # deletion/modification is handled via specific view logic, not generic perm.
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()

        return False