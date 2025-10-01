from django.db import models
from django.contrib.auth.models import User
from django.db.models.query import QuerySet


# --- Custom Manager ---
class UnreadMessagesManager(models.Manager):
    """
    Manager to handle queries specific to unread messages.
    """
    def get_queryset(self) -> QuerySet:
        return super().get_queryset()

    def for_user(self, user: User) -> QuerySet:
        return self.get_queryset().filter(
            receiver=user,
            read=False
        ).only('id', 'sender','receiver', 'content', 'timestamp', 'read')

# Model for messages between users
class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # NEW FIELD: Tracks if the message has ever been edited
    edited = models.BooleanField(default=False)

    parent_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies' # Use 'replies' to get all children of this message
    )

    read = models.BooleanField(default=False)

    # Managers
    objects = models.Manager()  # The default manager.
    unread = UnreadMessagesManager()  # Custom manager for unread messages.

    class Meta:
        ordering = ['-timestamp']

# Model for message history (to log edits)
class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Original Message'
    )
    # Stores the content of the message *before* the current save operation
    old_content = models.TextField(verbose_name='Previous Content')

    edited_at = models.DateTimeField(auto_now_add=True, verbose_name='Edited At')

    class Meta:
        ordering = ['-edited_at']
        verbose_name = 'Message History'
        verbose_name_plural = 'Message History'

# Notification model (from Task 0, included for completeness)
class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.OneToOneField(
        Message,
        on_delete=models.CASCADE,
        related_name='notification'
    )
    content = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']