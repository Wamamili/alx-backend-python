import django_filters
from .models import Message, Conversation

class MessageFilter(django_filters.FilterSet):
    """
    Filters for Message API:
    - filter by sender
    - filter by conversation
    - filter by sent_at range
    """
    sender = django_filters.CharFilter(field_name="sender__username", lookup_expr='icontains')
    conversation = django_filters.UUIDFilter(field_name="conversation__id")
    sent_after = django_filters.IsoDateTimeFilter(field_name="sent_at", lookup_expr='gte')
    sent_before = django_filters.IsoDateTimeFilter(field_name="sent_at", lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'sent_after', 'sent_before']


class ConversationFilter(django_filters.FilterSet):
    """
    Filter conversations by participant username or creation time range.
    """
    participant = django_filters.CharFilter(field_name="participants__username", lookup_expr='icontains')
    created_after = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_before = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr='lte')

    class Meta:
        model = Conversation
        fields = ['participant', 'created_after', 'created_before']
