# ticket_backend/apps/employees/admin.py
from django.contrib import admin
from .models import Employee, QuotaConfig


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'monthly_ticket_quota', 'current_month_tickets', 'remaining_quota')
    list_filter = ('department',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('current_month_tickets', 'last_quota_reset')
    
    def remaining_quota(self, obj):
        return obj.remaining_quota
    remaining_quota.short_description = 'Quota restant'


@admin.register(QuotaConfig)
class QuotaConfigAdmin(admin.ModelAdmin):
    list_display = ('default_quota', 'max_quota', 'ticket_value', 'employee_percentage', 'company_percentage')