# apps/core/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse

import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now


class CompanyMiddleware(MiddlewareMixin):
    """Middleware pour gérer l'entreprise active de l'utilisateur"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Si l'utilisateur a plusieurs entreprises (rare), on utilise la session
            if request.user.company:
                # L'utilisateur n'a qu'une seule entreprise
                request.current_company = request.user.company
            else:
                # L'utilisateur doit sélectionner son entreprise
                company_id = request.session.get('current_company_id')
                if company_id:
                    from apps.companies.models import Company
                    try:
                        request.current_company = Company.objects.get(id=company_id)
                    except Company.DoesNotExist:
                        request.current_company = None
                else:
                    request.current_company = None
        else:
            request.current_company = None


logger = logging.getLogger('django.request')

class RequestLogMiddleware(MiddlewareMixin):
    """Middleware pour logger toutes les requêtes"""
    
    def process_request(self, request):
        request.start_time = now()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = (now() - request.start_time).total_seconds() * 1000
            logger.info(f"{response.status_code} {request.method} {request.path} - {duration:.2f}ms")
        return response