# chats/middleware.py
import logging
from datetime import datetime

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
