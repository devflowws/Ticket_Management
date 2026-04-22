# apps/orders/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.employees.models import Employee
from apps.menus.models import DailyMenu


class MealOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        CONFIRMED = 'confirmed', 'Confirmé'
        PREPARING = 'preparing', 'En préparation'
        READY = 'ready', 'Prêt'
        DELIVERED = 'delivered', 'Livré'
        CANCELLED = 'cancelled', 'Annulé'
    
    class OrderType(models.TextChoices):
        NORMAL = 'normal', 'Commande normale'
        ANONYMOUS = 'anonymous', 'Commande anonyme'
        FOR_OTHER = 'for_other', 'Pour un tiers'
        OFF_MENU = 'off_menu', 'Hors menu'
    
    # Relations
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='orders'
    )
    menu = models.ForeignKey(
        DailyMenu, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='orders'
    )
    
    # Type de commande
    order_type = models.CharField(max_length=20, choices=OrderType.choices, default=OrderType.NORMAL)
    
    # Détails
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    
    # Commande hors menu
    off_menu_description = models.TextField(blank=True, help_text="Description si commande hors menu")
    off_menu_price = models.PositiveIntegerField(default=0, help_text="Prix en tickets")
    
    # Commande pour tiers
    for_person_name = models.CharField(max_length=200, blank=True, help_text="Nom de la personne si commande pour tiers")
    for_person_phone = models.CharField(max_length=50, blank=True)
    for_person_department = models.CharField(max_length=100, blank=True)
    
    # Statut
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Livraison
    delivery_notes = models.TextField(blank=True, help_text="Instructions de livraison")
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivered_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='delivered_orders')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['employee', 'status']),
        ]
    
    def __str__(self):
        if self.order_type == self.OrderType.ANONYMOUS:
            return f"Commande anonyme - {self.menu.title if self.menu else 'Hors menu'}"
        elif self.order_type == self.OrderType.FOR_OTHER:
            return f"Commande pour {self.for_person_name} - {self.menu.title if self.menu else 'Hors menu'}"
        return f"{self.employee.user.get_full_name() if self.employee else 'Inconnu'} - {self.menu.title if self.menu else 'Hors menu'}"
    
    def confirm(self):
        """Confirmer la commande"""
        if self.status == self.Status.PENDING:
            self.status = self.Status.CONFIRMED
            self.save()
            return True
        return False
    
    def mark_as_delivered(self, user):
        """Marquer comme livrée"""
        self.status = self.Status.DELIVERED
        self.delivered_at = timezone.now()
        self.delivered_by = user
        self.save()
    
    def cancel(self):
        """Annuler la commande"""
        if self.status in [self.Status.PENDING, self.Status.CONFIRMED]:
            self.status = self.Status.CANCELLED
            self.save()
            return True
        return False