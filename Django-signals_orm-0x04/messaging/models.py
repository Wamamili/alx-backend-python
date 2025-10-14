from django.db import models
from django.contrib.auth.models import User
from django.db.models import Prefetch

class UnreadMessagesManager(models.Manager):
    """Custom manager to retrieve only unread messages for a specific user."""
    def for_user(self, user):
        return self.filter(receiver=user, read=False).only('id', 'sender', 'receiver', 'content', 'timestamp')


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent_message = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    edited_by = models.ForeignKey(User, null=True, blank=True, related_name='edited_messages', on_delete=models.SET_NULL)
    read = models.BooleanField(default=False)

    # Custom manager for unread messages
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom unread messages manager

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"


class MessageHistory(models.Model):
    """Stores previous versions of edited messages."""
    original_message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for Message ID {self.original_message.id} at {self.edited_at}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"History of message {self.message.id} edited at {self.edited_at}"


# ✅ Custom manager for optimization using select_related and prefetch_related
class MessageManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related('sender', 'receiver', 'parent_message')
            .prefetch_related('replies', 'history')
        )

# Attach the optimized manager to Message
Message.objects = MessageManager()




