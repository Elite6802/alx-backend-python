
# messaging_app/chats/filters.py

import django_filters
from chats.models import Message, Conversation # Assume these models exist
from django.db.models import Q

class MessageFilter(django_filters.FilterSet):
    """
    Filter class for the Message model.
    Allows filtering by:
    - user_id: Messages in conversations involving a specific user.
    - min_date: Messages after or on a specific date/time.
    - max_date: Messages before or on a specific date/time.
    """

    # Filter by user participant in the conversation
    # Searches for messages belonging to conversations where the given user ID is a participant
    user_id = django_filters.NumberFilter(
        method='filter_by_participant',
        label='Participant User ID'
    )

    # Filter messages on or after a minimum timestamp
    min_date = django_filters.DateTimeFilter(
        field_name="timestamp",
        lookup_expr='gte',
        label='Minimum Date (YYYY-MM-DD HH:MM:SS)'
    )

    # Filter messages on or before a maximum timestamp
    max_date = django_filters.DateTimeFilter(
        field_name="timestamp",
        lookup_expr='lte',
        label='Maximum Date (YYYY-MM-DD HH:MM:SS)'
    )

    class Meta:
        model = Message
        # We only list the fields handled by the custom filter methods above
        fields = ['user_id', 'min_date', 'max_date']

    def filter_by_participant(self, queryset, name, value):
        """
        Custom method to filter messages based on a participant's ID
        in the message's conversation.
        """
        return queryset.filter(conversation__participants__id=value).distinct()

