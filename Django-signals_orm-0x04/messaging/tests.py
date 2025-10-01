# messaging/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class SignalTest(TestCase):
    def setUp(self):
        # Create two test users
        self.user1 = User.objects.create_user(username='sender', password='password1')
        self.user2 = User.objects.create_user(username='receiver', password='password2')

    def test_notification_created_on_new_message(self):
        """
        Tests that creating a new Message successfully triggers the signal
        to create a Notification for the receiver.
        """
        # Initial check
        self.assertEqual(Notification.objects.count(), 0)

        # Action: Create a new Message
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, this should notify you!"
        )

        # Verification: Notification count should be 1
        self.assertEqual(Notification.objects.count(), 1, "The signal failed to create a Notification.")

        # Further verification of content and linkage
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user2, "Notification user is incorrect.")
        self.assertTrue('Hello, this should notify you!' in notification.content, "Notification content is wrong.")

    def test_no_notification_on_message_update(self):
        """
        Tests that updating an existing Message does NOT trigger the signal
        to create a new Notification.
        """
        # Create an initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Initial content"
        )
        self.assertEqual(Notification.objects.count(), 1, "Initial notification should be present.")

        # Action: Update the existing message (post_save 'created' flag will be False)
        message.content = "Updated content"
        message.save()

        # Verification: Notification count must remain 1
        self.assertEqual(Notification.objects.count(), 1, "A new notification was incorrectly created on message update.")