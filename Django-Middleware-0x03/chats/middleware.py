import logging
from datetime import datetime
from django.http import HttpResponseForbidden
from django.http import JsonResponse

class OffensiveLanguageMiddleware:
    """
    Limits chat messages per IP: max 5 messages per minute.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Store timestamps per IP in memory (for production use, use Redis)
        self.ip_timestamps = {}

        # configuration
        self.time_window = 60  # seconds
        self.max_messages = 5

    def __call__(self, request):
        # Only track POST requests to chat endpoints
        if request.method == "POST" and request.path.startswith("/chats/"):
            ip = self._get_client_ip(request)
            now = time.time()
            timestamps = self.ip_timestamps.get(ip, [])

            # Keep only timestamps within the last minute
            timestamps = [t for t in timestamps if now - t < self.time_window]

            if len(timestamps) >= self.max_messages:
                return JsonResponse(
                    {"detail": f"Rate limit exceeded: max {self.max_messages} messages per minute"},
                    status=429
                )

            # record the current message
            timestamps.append(now)
            self.ip_timestamps[ip] = timestamps

        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

class RolePermissionMiddleware:
    """
    Middleware to restrict access to specific actions based on user roles.
    Only users with 'admin' or 'moderator' roles are allowed.
    """
    def __init__(self, get_response):
        """
        Initializes the middleware. get_response is the next middleware or the view.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        The main logic of the middleware. Executed on every request.
        """
        # 1. Check if the user is authenticated
        if not request.user.is_authenticated:
            # If the user isn't logged in, they are certainly not an admin/moderator.
            # Depending on your app, you might prefer an HTTP 401 (Unauthorized) here,
            # but for role-based permission enforcement, 403 (Forbidden) is appropriate.
            # We'll allow Django's default authentication/login system to handle
            # unauthenticated users for most views, but for simplicity here:
            return HttpResponseForbidden("Access Denied: You must be logged in.")

        # 2. Define the allowed roles
        # NOTE: You must have a way to access the user's role,
        # e.g., a custom field or groups. Assuming the user model has an 'role' attribute.
        allowed_roles = ['admin', 'moderator']
        user_role = getattr(request.user, 'role', 'default').lower() # Assumes a 'role' field on User model

        # 3. Enforce the role check
        # This middleware should only run on the views/paths where role is required.
        # For this example, we'll enforce it globally, so you might want to add
        # specific path filtering (e.g., if request.path.startswith('/admin/')).

        # If the user's role is NOT in the list of allowed roles, deny access.
        if user_role not in allowed_roles:
            return HttpResponseForbidden(f"Access Denied: Your role ('{user_role}') does not have permission for this action.")

        # 4. Pass the request to the next middleware or the view
        response = self.get_response(request)

        # 5. Return the response
        return response


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # configure logging to a file
        logging.basicConfig(
            filename="requests.log",
            level=logging.INFO,
            format="%(message)s"
        )

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logging.info(log_message)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour

        # Restrict access outside 6AM - 9PM
        if current_hour < 6 or current_hour >= 21:
            return HttpResponseForbidden(
                "<h1>403 Forbidden</h1><p>Chat access allowed only between 6AM and 9PM.</p>"
            )

        response = self.get_response(request)
        return response
