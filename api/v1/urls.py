# api/v1/urls.py
from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.accounts.urls')),
    path('employees/', include('apps.employees.urls')),
    path('providers/', include('apps.providers.urls')),
    path('tickets/', include('apps.tickets.urls')),
    path('purchases/', include('apps.purchases.urls')),
    path('validations/', include('apps.validations.urls')),
    path('consumptions/', include('apps.consumption.urls')),  
]