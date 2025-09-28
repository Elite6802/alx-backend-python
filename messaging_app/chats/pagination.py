# messaging_app/chats/pagination.py

from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages.
    Sets the page size to 20 messages.
    """
    page_size = 20
    # Optional: Allow client to override page size using a query parameter
    # page_size_query_param = 'page_size'
    # max_page_size = 100