# apps/providers/admin.py
from django.contrib import admin
from .models import Provider, ProviderSite, ProviderCategory


class ProviderSiteInline(admin.TabularInline):
    model = ProviderSite
    extra = 1
    fields = ['name', 'city', 'phone', 'is_active', 'is_main_site']


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'is_active', 'is_preferred', 'balance']
    list_filter = ['is_active', 'is_preferred', 'city']
    search_fields = ['name', 'commercial_name', 'email', 'phone']
    inlines = [ProviderSiteInline]
    readonly_fields = ['total_tickets_sold', 'total_amount_due', 'total_amount_paid', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'commercial_name', 'registration_number', 'tax_id')
        }),
        ('Contact', {
            'fields': ('contact_person', 'email', 'phone', 'alternative_phone')
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'country', 'postal_code')
        }),
        ('Contrat', {
            'fields': ('contract_number', 'contract_start', 'contract_end', 'contract_file')
        }),
        ('Statut', {
            'fields': ('is_active', 'is_preferred', 'rating')
        }),
        ('Finances', {
            'fields': ('total_tickets_sold', 'total_amount_due', 'total_amount_paid')
        }),
    )


@admin.register(ProviderSite)
class ProviderSiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'city', 'phone', 'is_active']
    list_filter = ['is_active', 'city', 'provider']
    search_fields = ['name', 'address', 'phone']


@admin.register(ProviderCategory)
class ProviderCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']