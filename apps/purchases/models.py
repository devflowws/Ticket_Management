# apps/purchases/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from apps.employees.models import Employee
from apps.accounts.models import User


class PurchaseRequest(models.Model):
    """Demande d'achat de tickets par un employé"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('En attente de validation')
        APPROVED = 'approved', _('Approuvé')
        REFUSED = 'refused', _('Refusé')
        CANCELLED = 'cancelled', _('Annulé')
    
    class PaymentMethod(models.TextChoices):
        MOOV = 'moov', _('Moov Money')
        MIXX_BY_YAS = 'mixx_by_yas', _('Mixx By Yas')
        FLOOZ = 'flooz', _('Flooz')
        BANK = 'bank', _('Virement bancaire')
        CASH = 'cash', _('Espèces')
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='purchase_requests'
    )
    quantity = models.PositiveIntegerField()
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices,
        blank=True
    )
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_proof = models.FileField(
        upload_to='payment_proofs/%Y/%m/%d/',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    
    # Montants
    ticket_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    employee_part = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    company_part = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_employee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_company_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Validation
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='validated_purchases'
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    refusal_reason = models.TextField(blank=True)
    validation_comment = models.TextField(blank=True)
    
    # Lot de tickets attribué
    ticket_lot = models.ForeignKey(
        'tickets.TicketLot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_request'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.user.email} - {self.quantity} tickets - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_value:
            from apps.employees.models import QuotaConfig
            config = QuotaConfig.get_active_config()
            self.ticket_value = config.ticket_value
            self.employee_part = self.ticket_value * config.employee_percentage / 100
            self.company_part = self.ticket_value * config.company_percentage / 100
        
        self.total_employee_amount = self.quantity * self.employee_part
        self.total_company_amount = self.quantity * self.company_part
        super().save(*args, **kwargs)
    
    def approve(self, validator, comment=''):
        from apps.tickets.models import TicketLot, Ticket
        from datetime import timedelta
        from apps.employees.models import QuotaConfig
        
        if self.status != self.Status.PENDING:
            raise ValueError(f"Cannot approve {self.status} request")
        
        config = QuotaConfig.get_active_config()
        
        # Créer le lot
        lot = TicketLot.objects.create(
            employee=self.employee,
            quantity=self.quantity,
            unit_value=self.ticket_value,
            employee_part=self.employee_part,
            company_part=self.company_part,
            expires_at=timezone.now() + timedelta(days=config.ticket_validity_days)
        )
        
        # Créer les tickets individuellement
        tickets = [Ticket(lot=lot) for _ in range(self.quantity)]
        Ticket.objects.bulk_create(tickets)
        
        # Mettre à jour la demande
        self.status = self.Status.APPROVED
        self.validated_by = validator
        self.validated_at = timezone.now()
        self.validation_comment = comment
        self.ticket_lot = lot
        self.save()
        
        # Mettre à jour le quota
        self.employee.current_month_tickets += self.quantity
        self.employee.save()
        
        return lot

        from apps.tickets.models import TicketLot
        from datetime import timedelta
        from apps.employees.models import QuotaConfig
        
        if self.status != self.Status.PENDING:
            raise ValueError(f"Cannot approve {self.status} request")
        
        config = QuotaConfig.get_active_config()
        
        lot = TicketLot.objects.create(
            employee=self.employee,
            quantity=self.quantity,
            unit_value=self.ticket_value,
            employee_part=self.employee_part,
            company_part=self.company_part,
            expires_at=timezone.now() + timedelta(days=config.ticket_validity_days)
        )
        
        self.status = self.Status.APPROVED
        self.validated_by = validator
        self.validated_at = timezone.now()
        self.validation_comment = comment
        self.ticket_lot = lot
        self.save()
        
        self.employee.current_month_tickets += self.quantity
        self.employee.save()
        
        return lot
    
    def refuse(self, validator, reason):
        if self.status != self.Status.PENDING:
            raise ValueError(f"Cannot refuse {self.status} request")
        
        self.status = self.Status.REFUSED
        self.validated_by = validator
        self.validated_at = timezone.now()
        self.refusal_reason = reason
        self.save()
    
    def cancel(self):
        if self.status == self.Status.PENDING:
            self.status = self.Status.CANCELLED
            self.save()