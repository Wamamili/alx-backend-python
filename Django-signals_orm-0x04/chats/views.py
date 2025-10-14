from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from rest_framework import viewsets, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from messaging.models import Message
from django.contrib.auth.models import User


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['participants__username']
    ordering_fields = ['created_at']

    def get_queryset(self):
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
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    pagination_class = MessagePagination
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at']

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(conversation__participants=user)

    def perform_create(self, serializer):
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


@cache_page(60)  # Cache this view for 60 seconds
@login_required
def conversation_messages(request, username):
    """Display messages between the logged-in user and another user."""
    other_user = get_object_or_404(User, username=username)

    # Retrieve all messages between the two users
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    context = {
        'messages': messages,
        'other_user': other_user
    }

    return render(request, 'chats/conversation.html', context)
