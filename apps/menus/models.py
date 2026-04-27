# apps/menus/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.providers.models import Provider
from apps.companies.models import Company
from datetime import time
import os


def menu_photo_path(instance, filename):
    """Génère le chemin de stockage des photos"""
    ext = filename.split('.')[-1]
    timestamp = int(timezone.now().timestamp())
    filename = f"{instance.provider.id}_{instance.id}_{timestamp}.{ext}"
    return os.path.join('menus', str(instance.provider.id), filename)


class MenuCategory(models.Model):
    """Catégorie de menu (Plat principal, Entrée, Boisson, Dessert)"""
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icône")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordre d'affichage")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='menu_categories', null=True, blank=True)
    
    class Meta:
        verbose_name = "Catégorie de menu"
        verbose_name_plural = "Catégories de menus"
        ordering = ['order']
    
    def __str__(self):
        return self.name


class Menu(models.Model):
    """Menu proposé par un prestataire"""
    
    class MealType(models.TextChoices):
        MAIN = 'main', 'Plat principal'
        STARTER = 'starter', 'Entrée'
        DESSERT = 'dessert', 'Dessert'
        DRINK = 'drink', 'Boisson'
        SIDE = 'side', 'Accompagnement'
    
    # Relations
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='menus', verbose_name="Prestataire")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='menus', null=True, blank=True, verbose_name="Entreprise")
    category = models.ForeignKey(MenuCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='menus', verbose_name="Catégorie")
    
    # Informations générales
    name = models.CharField(max_length=200, verbose_name="Nom du plat")
    description = models.TextField(blank=True, verbose_name="Description")
    meal_type = models.CharField(max_length=20, choices=MealType.choices, default=MealType.MAIN, verbose_name="Type de plat")
    
    # Prix
    price_tickets = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name="Prix en tickets")
    price_fcfa = models.PositiveIntegerField(default=0, verbose_name="Prix en FCFA")
    
    # Photos
    photo = models.ImageField(upload_to=menu_photo_path, null=True, blank=True, verbose_name="Photo principale")
    additional_photos = models.JSONField(default=list, blank=True, verbose_name="Photos supplémentaires")
    
    # Disponibilité
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    is_daily = models.BooleanField(default=False, verbose_name="Menu du jour")
    available_date = models.DateField(null=True, blank=True, verbose_name="Date de disponibilité")
    
    # Stock et commandes
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")
    max_per_order = models.PositiveIntegerField(default=10, verbose_name="Maximum par commande")
    max_orders_per_day = models.PositiveIntegerField(default=0, verbose_name="Maximum commandes par jour (0 = illimité)")
    
    # Horaires de commande - Utiliser time() pour éviter les problèmes de type
    order_start_time = models.TimeField(default=time(8, 0), verbose_name="Début des commandes")
    order_end_time = models.TimeField(default=time(10, 30), verbose_name="Fin des commandes")
    
    # Statistiques
    total_orders = models.PositiveIntegerField(default=0, verbose_name="Total commandes")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Note")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Menus"
        ordering = ['-is_daily', 'meal_type', 'name']
        indexes = [
            models.Index(fields=['provider', 'is_available']),
            models.Index(fields=['is_daily', 'available_date']),
            models.Index(fields=['meal_type']),
        ]
    
    def __str__(self):
        return f"{self.provider.name} - {self.name}"
    
    @property
    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None
    
    @property
    def can_order_now(self):
        """Vérifie si on peut commander maintenant"""
        now = timezone.now()
        current_time = now.time()
        return self.order_start_time <= current_time <= self.order_end_time
    
    @property
    def orders_count_today(self):
        return self.orders.filter(created_at__date=timezone.now().date()).count()
    
    @property
    def is_full_today(self):
        if self.max_orders_per_day == 0:
            return False
        return self.orders_count_today >= self.max_orders_per_day
    
    def increment_orders(self):
        self.total_orders += 1
        self.save(update_fields=['total_orders'])
    
    def decrement_stock(self, quantity):
        if self.stock > 0:
            self.stock -= quantity
            self.save(update_fields=['stock'])
            return True
        return False


class DailyMenu(models.Model):
    """Menu du jour"""
    
    MEAL_TYPE_CHOICES = [
        ('main', 'Plat principal'),
        ('starter', 'Entrée'),
        ('dessert', 'Dessert'),
        ('drink', 'Boisson'),
        ('side', 'Accompagnement'),
    ]
    
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='daily_menus')
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='main')
    
    price_tickets = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(50)])
    main_photo = models.ImageField(upload_to=menu_photo_path, null=True, blank=True)
    additional_photos = models.JSONField(default=list, blank=True)
    
    is_available = models.BooleanField(default=True)
    is_daily = models.BooleanField(default=False)
    max_orders_per_day = models.PositiveIntegerField(default=0, help_text="0 = illimité")
    
    # Utiliser time() au lieu de strings
    order_start_time = models.TimeField(default=time(8, 0))
    order_end_time = models.TimeField(default=time(10, 30))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-date', 'provider']
        indexes = [
            models.Index(fields=['date', 'is_available']),
            models.Index(fields=['provider', 'date']),
        ]
    
    def __str__(self):
        return f"{self.provider.name} - {self.title} - {self.date}"
    
    @property
    def can_order_now(self):
        """Vérifie si on peut commander maintenant"""
        now = timezone.now()
        if now.date() != self.date:
            return False
        current_time = now.time()
        return self.order_start_time <= current_time <= self.order_end_time
    
    @property
    def orders_count_today(self):
        return self.daily_orders.filter(created_at__date=self.date).count()
    
    @property
    def is_full(self):
        if self.max_orders_per_day == 0:
            return False
        return self.orders_count_today >= self.max_orders_per_day


class MenuDeadline(models.Model):
    """Heure limite de commande par jour"""
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
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='menu_deadlines', null=True, blank=True)
    
    class Meta:
        verbose_name = "Heure limite"
        verbose_name_plural = "Heures limites"
        ordering = ['weekday']
    
    def __str__(self):
        return f"{self.get_weekday_display()} - {self.deadline_time}"
    
    @classmethod
    def can_order_on_weekday(cls, weekday, current_time, company_id=None):
        """Vérifie si on peut commander à un jour/heure donné"""
        queryset = cls.objects.filter(weekday=weekday, is_active=True)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        try:
            deadline = queryset.get()
            return current_time <= deadline.deadline_time
        except cls.DoesNotExist:
            return True