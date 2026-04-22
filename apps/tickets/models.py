# apps/tickets/models.py
"""
Modèles pour la gestion des tickets
"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from apps.employees.models import Employee


class TicketStatus(models.TextChoices):
    """Statuts possibles d'un ticket"""
    ACTIVE = 'active', _('Actif')
    USED = 'used', _('Utilisé')
    EXPIRED = 'expired', _('Expiré')


class TicketLot(models.Model):
    """
    Lot (carnet) de tickets attribué à un employé
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='ticket_lots',
        verbose_name=_('employé')
    )
    quantity = models.PositiveIntegerField(_('quantité'), help_text=_('Nombre de tickets dans le lot'))
    unit_value = models.DecimalField(
        _('valeur unitaire'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Valeur monétaire d\'un ticket')
    )
    employee_part = models.DecimalField(
        _('part employé'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Montant payé par l\'employé par ticket')
    )
    company_part = models.DecimalField(
        _('part entreprise'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Montant payé par l\'entreprise par ticket')
    )
    total_amount = models.DecimalField(
        _('montant total'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Montant total du lot')
    )
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    expires_at = models.DateTimeField(_('date d\'expiration'), help_text=_('Date à laquelle les tickets expirent'))
    
    class Meta:
        verbose_name = _('lot de tickets')
        verbose_name_plural = _('lots de tickets')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Lot {self.id} - {self.employee} - {self.quantity} tickets"
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.quantity * self.unit_value
        super().save(*args, **kwargs)
    
    @property
    def used_count(self):
        """Nombre de tickets utilisés dans ce lot"""
        return self.tickets.filter(status=TicketStatus.USED).count()
    
    @property
    def active_count(self):
        """Nombre de tickets actifs dans ce lot"""
        return self.tickets.filter(status=TicketStatus.ACTIVE).count()
    
    @property
    def expired_count(self):
        """Nombre de tickets expirés dans ce lot"""
        return self.tickets.filter(status=TicketStatus.EXPIRED).count()


class Ticket(models.Model):
    """
    Ticket individuel
    """
    lot = models.ForeignKey(
        TicketLot,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name=_('lot')
    )
    unique_code = models.CharField(
        _('code unique'),
        max_length=50,
        unique=True,
        default=uuid.uuid4,
        editable=False
    )
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.ACTIVE
    )
    used_at = models.DateTimeField(_('date d\'utilisation'), null=True, blank=True)
    # Commenté temporairement car l'app consumption n'existe pas encore
    # used_by = models.ForeignKey(
    #     'consumption.Consumption',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='tickets_used',
    #     verbose_name=_('utilisé dans')
    # )
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('ticket')
        verbose_name_plural = _('tickets')
        ordering = ['lot__created_at', 'id']
    
    def __str__(self):
        return f"Ticket {self.unique_code[:8]} - {self.status}"
    
    def use(self, consumption=None):
        """Utilise le ticket"""
        if self.status != TicketStatus.ACTIVE:
            raise ValueError(f"Impossible d'utiliser un ticket {self.status}")
        
        if self.is_expired:
            self.status = TicketStatus.EXPIRED
            self.save()
            raise ValueError("Ce ticket a expiré")
        
        self.status = TicketStatus.USED
        self.used_at = timezone.now()
        # if consumption:
        #     self.used_by = consumption
        self.save()
    
    @property
    def is_expired(self):
        """Vérifie si le ticket a expiré"""
        return timezone.now() > self.lot.expires_at
    
    def mark_as_expired(self):
        """Marque le ticket comme expiré"""
        if self.status == TicketStatus.ACTIVE and self.is_expired:
            self.status = TicketStatus.EXPIRED
            self.save()
            return True
        return False


class EmployeeBalance(models.Model):
    """
    Vue ou modèle pour suivre le solde des employés
    """
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='balance',
        verbose_name=_('employé')
    )
    active_tickets = models.PositiveIntegerField(_('tickets actifs'), default=0)
    used_tickets_month = models.PositiveIntegerField(_('tickets utilisés ce mois'), default=0)
    last_updated = models.DateTimeField(_('dernière mise à jour'), auto_now=True)
    
    class Meta:
        verbose_name = _('solde employé')
        verbose_name_plural = _('soldes employés')
    
    def __str__(self):
        return f"Solde {self.employee}: {self.active_tickets} tickets"
    
    def update_balance(self):
        """Met à jour le solde à partir des tickets réels"""
        self.active_tickets = Ticket.objects.filter(
            lot__employee=self.employee,
            status=TicketStatus.ACTIVE
        ).count()
        self.save()