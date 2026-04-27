from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.companies.views import CompanyListView

# Imports des vues core
from apps.core.views import (
    landing_page, register_company, login_view, logout_view, profile_view,
    change_password_view, admin_dashboard, employee_dashboard, validator_dashboard,
    finance_dashboard, provider_dashboard, provider_menus, provider_transactions, provider_orders,
    my_balance, purchase_request_create,
    my_orders, pending_validations, validation_history, reports_dashboard,
    provider_payment, provider_list, menu_list, order_menu, select_company, order_meal, my_tickets
)

# Imports des vues API admin
from apps.core.api_views import (
    api_add_user, api_edit_user, api_delete_user,
    api_add_provider, api_edit_provider, api_delete_provider,
    api_generate_ticket_lot
)


# Import de quota_config
from apps.companies.views import quota_config  # Ajouter cette ligne

schema_view = get_schema_view(
    openapi.Info(
        title="Systeme de gestion des tickets API",
        default_version='v1',
        description="API de gestion des tickets repas",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
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
    
    # Frontend - Page d'accueil publique
    path('', landing_page, name='landing'),
    path('register-company/', register_company, name='register_company'),
    
    # Frontend Auth
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password_view, name='change_password'),
    
    # Dashboards
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/employee/', employee_dashboard, name='employee_dashboard'),
    path('dashboard/validator/', validator_dashboard, name='validator_dashboard'),
    path('dashboard/finance/', finance_dashboard, name='finance_dashboard'),
    path('dashboard/provider/', provider_dashboard, name='provider_dashboard'),
    path('dashboard/provider/menus/', provider_menus, name='provider_menus'),
    path('dashboard/provider/transactions/', provider_transactions, name='provider_transactions'),
    path('dashboard/provider/orders/', provider_orders, name='provider_orders'),

    # Configuration
    path('admin/quota-config/', quota_config, name='quota_config'),
    
    # Tickets
    path('tickets/balance/', my_balance, name='my_balance'),
    path('tickets/my/', my_tickets, name='my_tickets'),
    
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
    path('order-meal/', order_meal, name='order_meal'),
    path('orders/menu/', order_meal, name='orders_menu'),

    path('api/companies/', CompanyListView.as_view(), name='company_list'),

    # Ajouter dans urlpatterns
    path('api/admin/add-user/', api_add_user, name='api_add_user'),
    path('api/admin/edit-user/<int:user_id>/', api_edit_user, name='api_edit_user'),
    path('api/admin/delete-user/<int:user_id>/', api_delete_user, name='api_delete_user'),
    path('api/admin/add-provider/', api_add_provider, name='api_add_provider'),
    path('api/admin/edit-provider/<int:provider_id>/', api_edit_provider, name='api_edit_provider'),
    path('api/admin/delete-provider/<int:provider_id>/', api_delete_provider, name='api_delete_provider'),
    path('api/admin/generate-lot/', api_generate_ticket_lot, name='api_generate_lot'),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)