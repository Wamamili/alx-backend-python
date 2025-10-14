from django.db import models

class UnreadMessagesManager(models.Manager):
    """Custom manager to retrieve only unread messages for a specific user."""
    def unread_for_user(self, user):
        # Returns unread messages for a specific user, optimized with .only()
        return self.filter(receiver=user, read=False).only(
            'id', 'sender', 'receiver', 'content', 'timestamp'
        )
