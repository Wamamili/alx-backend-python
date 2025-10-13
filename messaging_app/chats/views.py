from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from messaging_app.chats.permissions import IsParticipantOrReadOnly
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsParticipantOrReadOnly]

    """
    ViewSet for managing user conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants__username', 'participants__email']

    def get_queryset(self):
        """
        Limit conversations to those that include the current authenticated user.
        """
        return self.queryset.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically add the creator to the conversation participants.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        conversation.save()
        return conversation

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """
        Custom action to send a message within a conversation.
        """
        conversation = get_object_or_404(Conversation, pk=pk)
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user, conversation=conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body', 'sender__username', 'conversation__id']
    ordering_fields = ['sent_at']

    def get_queryset(self):
        """
        Restrict messages to conversations that the user participates in.
        """
        return self.queryset.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        """
        Assign the authenticated user as the sender of the message.
        """
        serializer.save(sender=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
