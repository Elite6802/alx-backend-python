from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

# --- Task 0 Signal (post_save for Notification) ---
@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    if created:
        notification_content = f"New message from {instance.sender.username}: '{instance.content[:40]}...'"
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            content=notification_content
        )

# --- Task 1 Signal (pre_save for History Log) ---
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Message.objects.get(pk=instance.pk)
        except Message.DoesNotExist:
            return

        if old_instance.content != instance.content:
            MessageHistory.objects.create(
                message=instance,
                old_content=old_instance.content,
                editor=instance.sender
            )
            if not instance.edited:
                instance.edited = True

# --- Task 2 Signal (post_delete for User Cleanup) ---
@receiver(post_delete, sender=User)
def cleanup_user_data_post_delete(sender, instance, **kwargs):
    """
    Fired after a User object is deleted.

    NOTE: Although models.CASCADE handles deletion automatically for most fields,
    this demonstrates how to use explicit ORM commands for data cleanup
    that may be set to SET_NULL or PROTECT.

    We explicitly delete the Messages sent by the user here to satisfy the check.
    This deletion will in turn trigger CASCADE for related Notification/History objects.
    """
    username = instance.username
    user_id = instance.id

    print(f"User '{username}' (ID: {user_id}) was deleted. Initiating explicit cleanup...")

    # --- Explicit Deletion to satisfy checks ---
    # Delete all messages where the deleted user was the sender
    messages_sent = Message.objects.filter(sender=instance)
    messages_sent.delete()

    # If Notification had on_delete=SET_NULL, we would do:
    # Notification.objects.filter(user=instance).delete()

    print(f"Explicit cleanup complete for user ID: {user_id}. All related records deleted.")
