# chats/middleware.py
import logging
from datetime import datetime
from django.http import HttpResponseForbidden

class RequestLoggingMiddleware:
    """
    Middleware that logs each user’s request with timestamp, user, and path.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Configure logger
        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler("requests.log")
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        # Get user info
        user = request.user if request.user.is_authenticated else "AnonymousUser"
        # Log details
        self.logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        # Continue processing request
        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the chat app outside 6PM to 9PM.
    Returns 403 Forbidden if accessed outside allowed hours.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour

        # Allow access only between 18 (6 PM) and 21 (9 PM)
        if current_hour < 18 or current_hour >= 21:
            return HttpResponseForbidden(
                "Access to the chat is restricted outside 6PM–9PM hours."
            )

        return self.get_response(request)
