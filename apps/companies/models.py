# apps/companies/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    name = models.CharField(_('nom'), max_length=200)
    email = models.EmailField(_('email'), unique=True)
    phone = models.CharField(_('téléphone'), max_length=50, blank=True)
    address = models.TextField(_('adresse'), blank=True)
    city = models.CharField(_('ville'), max_length=100, blank=True)
    country = models.CharField(_('pays'), max_length=100, default='Togo')
    
    ticket_value = models.DecimalField(_('valeur du ticket'), max_digits=10, decimal_places=2, default=1000)
    employee_percentage = models.DecimalField(_('part employé (%)'), max_digits=5, decimal_places=2, default=40)
    company_percentage = models.DecimalField(_('part entreprise (%)'), max_digits=5, decimal_places=2, default=60)
    default_quota = models.PositiveIntegerField(_('quota mensuel'), default=30)
    ticket_validity_days = models.PositiveIntegerField(_('validité tickets'), default=90)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Entreprise'
        verbose_name_plural = 'Entreprises'
    
    def __str__(self):
        return self.name