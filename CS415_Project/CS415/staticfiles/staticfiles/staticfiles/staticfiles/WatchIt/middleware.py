import logging

logger = logging.getLogger('WatchIt')

class ActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            logger.info(f"User {request.user.username} accessed {request.path}")
        else:
            logger.info(f"Unauthenticated user accessed {request.path}")
        return response