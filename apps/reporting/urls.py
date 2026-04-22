# apps/reporting/urls.py
from django.urls import path
from .views import MonthlyReportView, ProviderSummaryView, EmployeeSummaryView, ExportView

urlpatterns = [
    path('monthly/', MonthlyReportView.as_view(), name='monthly-report'),
    path('providers/', ProviderSummaryView.as_view(), name='provider-summary'),
    path('employees/', EmployeeSummaryView.as_view(), name='employee-summary'),
    path('export/', ExportView.as_view(), name='export'),
]