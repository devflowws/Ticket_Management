from django.db import models
from django.utils import timezone
from apps.employees.models import Employee
from apps.providers.models import Provider


class ConsumptionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        CONFIRMED = 'confirmed', 'Confirmé'
        REJECTED = 'rejected', 'Rejeté'
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='consumption_requests')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='consumption_requests')
    nb_tickets = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee} - {self.nb_tickets} tickets - {self.status}"
    
    def confirm(self, user):
        from apps.tickets.models import Ticket
        
        if self.status != self.Status.PENDING:
            raise ValueError("Seule une demande en attente peut être confirmée")
        
        # Vérifier le solde
        active_tickets = Ticket.objects.filter(
            lot__employee=self.employee,
            status='active'
        ).count()
        
        if active_tickets < self.nb_tickets:
            raise ValueError(f"Solde insuffisant. Disponible: {active_tickets}")
        
        # Déduire les tickets
        tickets = Ticket.objects.filter(
            lot__employee=self.employee,
            status='active'
        )[:self.nb_tickets]
        
        for ticket in tickets:
            ticket.status = 'used'
            ticket.used_at = timezone.now()
            ticket.save()
        
        # Mettre à jour la demande
        self.status = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()
        self.confirmed_by = user
        self.save()
        
        # Mettre à jour le solde
        self.employee.balance.update_balance()
        
        return True
    
    def reject(self, user, reason=""):
        self.status = self.Status.REJECTED
        self.confirmed_at = timezone.now()
        self.confirmed_by = user
        self.save()