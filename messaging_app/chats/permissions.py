from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only authenticated users who are participants
    of a conversation to view, send, update, or delete messages.
    """

    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # For conversation objects
        if hasattr(obj, 'participants'):
            return user in obj.participants.all()

        # For message objects
        if hasattr(obj, 'conversation'):
            if user in obj.conversation.participants.all():
                # Allow only sender to edit/delete their own messages
                if request.method in ['PUT', 'PATCH', 'DELETE']:
                    return obj.sender == user
                return True
        return False
