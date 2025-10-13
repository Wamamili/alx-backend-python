from rest_framework import permissions

class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Only participants of a conversation
    can view or send messages in it.
    """

    def has_object_permission(self, request, view, obj):
        # For conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        # For message objects
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return False
