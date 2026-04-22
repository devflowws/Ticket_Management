# apps/consumption/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.employees.models import Employee
from apps.providers.models import Provider, ProviderSite


class Consumption(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='consumptions')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='consumptions')
    site = models.ForeignKey(ProviderSite, on_delete=models.SET_NULL, null=True, blank=True)
    nb_tickets = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    company_part = models.DecimalField(max_digits=10, decimal_places=2)
    employee_part = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.employee} - {self.nb_tickets} tickets"