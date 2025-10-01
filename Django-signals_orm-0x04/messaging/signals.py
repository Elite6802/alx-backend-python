from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.contrib.auth.models import User

# --- Task 0 Signal (post_save) ---
@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Signal handler that listens for a new Message and creates a Notification
    for the receiver user.
    """
    # Only run this logic if a new Message object was created (not updated)
    if created:
        notification_content = f"New message from {instance.sender.username}: '{instance.content[:40]}...'"

        # Create the Notification for the user who received the message
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            content=notification_content
        )
# --- End of Task 0 Signal ---

# --- Task 1 Signal (pre_save) ---
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Captures the old content of a Message before it is saved (updated)
    and logs it in MessageHistory.
    """
    # Check if the instance already exists in the database (i.e., it's an UPDATE, not a CREATE)
    if instance.pk:
        try:
            # Retrieve the existing object from the database
            old_instance = Message.objects.get(pk=instance.pk)
        except Message.DoesNotExist:
            # Should not happen in an update, but good for robustness
            return

        # Check if the content has actually changed
        if old_instance.content != instance.content:
            # 1. Log the OLD content
            MessageHistory.objects.create(
                message=instance,
                old_content=old_instance.content
            )
            # 2. Mark the message as edited (only necessary if not already true)
            if not instance.edited:
                instance.edited = True
# --- End of Task 1 Signal ---

# --- Task 2 Signal (post_delete) ---
@receiver(post_delete, sender=User)
def cleanup_user_data_post_delete(sender, instance, **kwargs):
    """
    Fired after a User object is deleted.
    Used here primarily for logging or deleting non-cascading data (e.g., files).

    NOTE: All models with ForeignKey(User, on_delete=models.CASCADE)
    (like Message, Notification, History) are already deleted by the database.
    This signal confirms the cleanup process.
    """
    username = instance.username
    user_id = instance.id

    print(f"User '{username}' (ID: {user_id}) was deleted. Initiating final cleanup...")
    print(f"Cleanup finished for user ID: {user_id}. All related database records were handled by CASCADE.")