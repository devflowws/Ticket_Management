# ticket_backend/apps/tickets/urls.py
"""
URLs pour l'application tickets
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketLotViewSet, TicketViewSet, EmployeeBalanceView, ExpireTicketsView, EmployeeTicketStatsViewSet

router = DefaultRouter()
router.register(r'lots', TicketLotViewSet)
router.register(r'', TicketViewSet)
router.register(r'stats', EmployeeTicketStatsViewSet, basename='employee-ticket-stats')

urlpatterns = [
    path('', include(router.urls)),
    path('balance/<int:employee_id>/', EmployeeBalanceView.as_view(), name='employee-balance'),
    path('expire/', ExpireTicketsView.as_view(), name='expire-tickets'),
]