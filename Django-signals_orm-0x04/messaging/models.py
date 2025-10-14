from django.db import models
from django.contrib.auth.models import User
from django.db.models import Prefetch


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, null=True, blank=True, related_name='edited_messages', on_delete=models.SET_NULL)
    parent_message = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        if self.parent_message:
            return f"Reply by {self.sender} to message {self.parent_message.id}"
        return f"Message from {self.sender} to {self.receiver}"

    # ✅ Recursive method to fetch all replies in a threaded structure
    def get_all_replies(self):
        replies = []
        for reply in self.replies.all().select_related('sender', 'receiver').prefetch_related('replies'):
            replies.append(reply)
            replies.extend(reply.get_all_replies())
        return replies

    class Meta:
        ordering = ['timestamp']


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
