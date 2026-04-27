# apps/reporting/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MonthlyReportView, ProviderSummaryView, EmployeeSummaryView, ExportView, FinanceStatsViewSet

router = DefaultRouter()
router.register(r'stats', FinanceStatsViewSet, basename='finance-stats')

urlpatterns = [
    path('', include(router.urls)),
    path('monthly/', MonthlyReportView.as_view(), name='monthly-report'),
    path('providers/', ProviderSummaryView.as_view(), name='provider-summary'),
    path('employees/', EmployeeSummaryView.as_view(), name='employee-summary'),
    path('export/', ExportView.as_view(), name='export'),
]