import time
from datetime import datetime
from django.http import JsonResponse
from collections import defaultdict
import logging

# Configure logging for requests
logger = logging.getLogger(__name__)
handler = logging.FileHandler("requests.log")
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    """
    Logs each request with timestamp, user, and path.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """
    Restrict chat access between 6AM and 9PM only.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        # Restrict between 9PM (21) and 6AM (6)
        if current_hour >= 21 or current_hour < 6:
            return JsonResponse(
                {"error": "Access restricted. Chat is available between 6 AM and 9 PM."},
                status=403
            )
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Limits number of POST requests (messages) from a single IP to 5 per minute.
    """
    request_log = defaultdict(list)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST":
            ip = self.get_client_ip(request)
            current_time = time.time()

            # Clean up old entries (older than 60 seconds)
            self.request_log[ip] = [
                t for t in self.request_log[ip] if current_time - t < 60
            ]

            # Check request count
            if len(self.request_log[ip]) >= 5:
                return JsonResponse(
                    {"error": "Rate limit exceeded: Max 5 messages per minute allowed."},
                    status=403
                )

            # Record this request timestamp
            self.request_log[ip].append(current_time)

        return self.get_response(request)

    def get_client_ip(self, request):
        """
        Extracts the real client IP address.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


from django.http import JsonResponse

class RolepermissionMiddleware:
    """
    Middleware to enforce role-based permissions.
    Only users with the role 'admin' or 'moderator' are allowed to access specific actions.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define restricted methods
        restricted_methods = ["PUT", "PATCH", "DELETE"]

        # Only check permissions for authenticated users
        if request.user.is_authenticated and request.method in restricted_methods:
            user_role = getattr(request.user, "role", "user")  # assumes User model has a 'role' field

            if user_role not in ["admin", "moderator"]:
                return JsonResponse(
                    {"error": "Permission denied. Only admins and moderators can perform this action."},
                    status=403
                )

        return self.get_response(request)
