from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Conversations.
    - List all conversations for the logged-in user
    - Create new conversations
    - View a specific conversation and its messages
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants__username', 'participants__email']

    def get_queryset(self):
        """
        Return conversations only for the current authenticated user.
        """
        user = self.request.user
        return Conversation.objects.filter(participants=user)

    def perform_create(self, serializer):
        """
        Automatically include the current user as a participant when creating a conversation.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Custom action to get all messages under a conversation.
        Only participants can view messages.
        """
        conversation = self.get_object()
        user = request.user

        if user not in conversation.participants.all():
            return Response(
                {"detail": "Access denied. You are not a participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        messages = Message.objects.filter(conversation_id=pk).order_by('sent_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Messages.
    - List all messages for the user's conversations
    - Create new messages within a conversation
    - Restrict edits/deletes to the sender
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    search_fields = ['message_body', 'sender__username']

    def get_queryset(self):
        """
        Return only messages from conversations where the user is a participant.
        """
        user = self.request.user
        return Message.objects.filter(conversation__participants=user)

    def perform_create(self, serializer):
        """
        Ensure the user is a participant before sending a message.
        """
        conversation = serializer.validated_data.get('conversation')
        user = self.request.user

        if user not in conversation.participants.all():
            return Response(
                {"detail": "Access denied. You are not part of this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.save(sender=user)

    def update(self, request, *args, **kwargs):
        """
        Allow only message sender to update their message.
        """
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {"detail": "You can only edit your own messages."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Allow only message sender to delete their message.
        """
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {"detail": "You can only delete your own messages."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
