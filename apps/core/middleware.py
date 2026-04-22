# apps/core/middleware.py
import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now

logger = logging.getLogger('django.request')


class RequestLogMiddleware(MiddlewareMixin):
    """Middleware pour logger toutes les requêtes"""
    
    def process_request(self, request):
        request.start_time = now()
        logger.debug(f"→ {request.method} {request.path} - {request.user if request.user.is_authenticated else 'Anonymous'}")
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = (now() - request.start_time).total_seconds() * 1000
            status_color = "\033[92m" if 200 <= response.status_code < 300 else "\033[91m"
            reset_color = "\033[0m"
            logger.info(
                f"← {status_color}{response.status_code}{reset_color} {request.method} {request.path} - "
                f"{duration:.2f}ms"
            )
        return response