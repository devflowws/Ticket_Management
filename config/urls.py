# config/urls.py - Version simplifiée et stable
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Import des vues core
from apps.core.views import login_view, logout_view, profile_view, change_password_view

from apps.core.views import (
    landing_page, register_company, login_view, logout_view, profile_view, 
    change_password_view, admin_dashboard, employee_dashboard, validator_dashboard, 
    finance_dashboard, my_balance, purchase_request_create, my_orders, 
    pending_validations, validation_history, reports_dashboard, provider_payment, 
    provider_list, menu_list
)

schema_view = get_schema_view(
    openapi.Info(
        title="Systeme de gestion des tickets API",
        default_version='v1',
        description="API de gestion des tickets repas",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Vues dashboard (seront importées dynamiquement pour éviter les erreurs)
def get_dashboard_views():
    try:
        from apps.dashboard.views import (
            admin_dashboard, employee_dashboard, 
            validator_dashboard, finance_dashboard
        )
        return admin_dashboard, employee_dashboard, validator_dashboard, finance_dashboard
    except ImportError:
        # Vues par défaut si dashboard n'existe pas
        from django.shortcuts import render
        def default_dashboard(request):
            return render(request, 'base/base.html')
        return default_dashboard, default_dashboard, default_dashboard, default_dashboard

admin_dash, emp_dash, val_dash, fin_dash = get_dashboard_views()

# Vues supplémentaires
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def my_balance(request):
    return render(request, 'tickets/balance.html')

@login_required
def purchase_request_create(request):
    return render(request, 'purchases/create.html')

@login_required
def my_orders(request):
    return render(request, 'orders/list.html')

@login_required
def pending_validations(request):
    return render(request, 'validations/pending.html')

@login_required
def validation_history(request):
    return render(request, 'validations/history.html')

@login_required
def reports_dashboard(request):
    return render(request, 'reports/dashboard.html')

@login_required
def provider_payment(request):
    return render(request, 'reports/provider_payment.html')

@login_required
def provider_list(request):
    return render(request, 'providers/list.html')

@login_required
def menu_list(request):
    return render(request, 'menus/list.html')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ajouter ces lignes dans urlpatterns
    path('', landing_page, name='landing'),
    path('register-company/', register_company, name='register_company'),
    
    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API
    path('api/auth/', include('apps.accounts.urls')),
    path('api/employees/', include('apps.employees.urls')),
    path('api/providers/', include('apps.providers.urls')),
    path('api/tickets/', include('apps.tickets.urls')),
    path('api/purchases/', include('apps.purchases.urls')),
    path('api/validations/', include('apps.validations.urls')),
    path('api/consumption-requests/', include('apps.consumption_requests.urls')),
    path('api/menus/', include('apps.menus.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/reports/', include('apps.reporting.urls')),
    
    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Frontend Auth
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password_view, name='change_password'),
    
    # Dashboards
    path('dashboard/', admin_dash, name='dashboard'),
    path('admin/dashboard/', admin_dash, name='admin_dashboard'),
    path('employee/dashboard/', emp_dash, name='employee_dashboard'),
    path('validator/dashboard/', val_dash, name='validator_dashboard'),
    path('finance/dashboard/', fin_dash, name='finance_dashboard'),
    
    # Tickets
    path('tickets/balance/', my_balance, name='my_balance'),
    
    # Purchases
    path('purchases/create/', purchase_request_create, name='purchase_request_create'),
    
    # Orders
    path('orders/my/', my_orders, name='my_orders'),
    
    # Validations
    path('validations/pending/', pending_validations, name='pending_validations'),
    path('validations/history/', validation_history, name='validation_history'),
    
    # Reports
    path('reports/dashboard/', reports_dashboard, name='reports_dashboard'),
    path('reports/provider-payment/', provider_payment, name='provider_payment'),
    
    # Providers
    path('providers/', provider_list, name='provider_list'),
    
    # Menus
    path('menus/', menu_list, name='menu_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)