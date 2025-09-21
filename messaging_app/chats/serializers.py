from rest_framework import serializers
from .models import User, Conversation, Message


# -------------------
# User Serializer
# -------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "user_id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
        ]


# -------------------
# Message Serializer
# -------------------
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)       # nested sender info
    recipient = UserSerializer(read_only=True)    # nested recipient info

    class Meta:
        model = Message
        fields = [
            "message_id",
            "conversation",
            "sender",
            "recipient",
            "message_body",
            "sent_at",
        ]


# -------------------
# Conversation Serializer
# -------------------
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)   # show participants
    messages = MessageSerializer(many=True, read_only=True)    # show messages

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "created_at",
            "messages",
        ]
