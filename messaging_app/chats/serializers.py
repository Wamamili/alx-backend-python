from rest_framework import serializers
from .models import User, Conversation, Message


# -------------------
# User Serializer
# -------------------
class UserSerializer(serializers.ModelSerializer):
    # Explicit CharFields for first & last name
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)

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
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)

    # Example: computed field
    short_preview = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "conversation",
            "sender",
            "recipient",
            "message_body",
            "short_preview",
            "sent_at",
        ]

    def get_short_preview(self, obj):
        """Return a short preview of the message body."""
        return obj.message_body[:30] + ("..." if len(obj.message_body) > 30 else "")

    def validate_message_body(self, value):
        """Ensure message body is not empty or whitespace only."""
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value


# -------------------
# Conversation Serializer
# -------------------
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    # Computed field: total participants
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participant_count",
            "created_at",
            "messages",
        ]

    def get_participant_count(self, obj):
        """Count how many users are in the conversation."""
        return obj.participants.count()
