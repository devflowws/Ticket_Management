# apps/menus/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.providers.models import Provider
import os


def menu_photo_path(instance, filename):
    """Génère le chemin de stockage des photos"""
    ext = filename.split('.')[-1]
    filename = f"{instance.provider.id}_{instance.date}_{timezone.now().timestamp()}.{ext}"
    return os.path.join('menus', str(instance.date.year), str(instance.date.month), filename)


class DailyMenu(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='menus')
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Prix en tickets
    price_tickets = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="Nombre de tickets requis"
    )
    
    # Photos (support multiple)
    main_photo = models.ImageField(
        upload_to=menu_photo_path,
        null=True,
        blank=True,
        help_text="Photo principale du menu"
    )
    additional_photos = models.JSONField(default=list, blank=True, help_text="Photos supplémentaires (URLs)")
    
    # Disponibilité
    is_available = models.BooleanField(default=True)
    max_orders_per_day = models.PositiveIntegerField(default=0, help_text="0 = illimité")
    
    # Horaires
    order_start_time = models.TimeField(default='08:00', help_text="Début des commandes")
    order_end_time = models.TimeField(default='10:30', help_text="Fin des commandes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-date', 'provider']
        unique_together = ['provider', 'date']
        indexes = [
            models.Index(fields=['date', 'is_available']),
            models.Index(fields=['provider', 'date']),
        ]
    
    def __str__(self):
        return f"{self.provider.name} - {self.title} - {self.date}"
    
    @property
    def can_order_now(self):
        """Vérifie si on peut encore commander"""
        now = timezone.now()
        if now.date() != self.date:
            return False
        current_time = now.time()
        return self.order_start_time <= current_time <= self.order_end_time
    
    @property
    def orders_count_today(self):
        return self.orders.filter(created_at__date=self.date).count()
    
    @property
    def is_full(self):
        if self.max_orders_per_day == 0:
            return False
        return self.orders_count_today >= self.max_orders_per_day


class MenuDeadline(models.Model):
    WEEKDAYS = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]
    
    weekday = models.IntegerField(choices=WEEKDAYS, unique=True)
    deadline_time = models.TimeField(help_text="Heure limite de commande")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['weekday']
    
    def __str__(self):
        return f"{self.get_weekday_display()} - {self.deadline_time}"
    
    @classmethod
    def can_order_on_weekday(cls, weekday, current_time):
        """Vérifie si on peut commander à un jour/heure donné"""
        try:
            deadline = cls.objects.get(weekday=weekday, is_active=True)
            return current_time <= deadline.deadline_time
        except cls.DoesNotExist:
            return True


class MenuCategory(models.Model):
    """Catégorie de menu (Petit-déjeuner, Déjeuner, Dîner)"""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name