from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'country', 'is_active', 'created_at')
    list_filter = ('is_active', 'country', 'created_at')
    search_fields = ('name', 'email', 'phone')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'email', 'phone', 'address', 'city', 'country', 'is_active')
        }),
        ('Configuration des tickets', {
            'fields': ('ticket_value', 'employee_percentage', 'company_percentage', 'default_quota', 'ticket_validity_days')
        }),
    )
