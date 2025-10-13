from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


# -------------------------------------------------------
# Conversation ViewSet
# -------------------------------------------------------
class ConversationViewSet(viewsets.ModelViewSet):
    """
    Handles listing, retrieving, and creating conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return only conversations where the authenticated user is a participant.
        """
        return self.queryset.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically include the authenticated user in the conversation participants.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        conversation.save()
        return conversation

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """
        Custom action to send a message to an existing conversation.
        """
        conversation = get_object_or_404(Conversation, pk=pk)
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user, conversation=conversation)
        return Response(serializer.data)


# -------------------------------------------------------
# Message ViewSet
# -------------------------------------------------------
class MessageViewSet(viewsets.ModelViewSet):
    """
    Handles listing and sending messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return messages only from conversations the authenticated user is part of.
        """
        return self.queryset.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        """
        Allow sending a message and automatically attach the user as sender.
        """
        serializer.save(sender=self.request.user)
