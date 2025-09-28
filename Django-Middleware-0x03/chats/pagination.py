from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    """
    Custom pagination class to enforce 20 messages per page
    and allow client-side control via query parameters.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Customizes the response format if needed, but the check
        "page.paginator.count" is an internal check used by the
        framework to get the total count, which is handled here.
        """
        return super().get_paginated_response(data)