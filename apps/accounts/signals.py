# ticket_backend/apps/accounts/signals.py
"""
Signaux pour l'application accounts
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil employé quand un utilisateur est créé avec le rôle employé"""
    if created and instance.role == 'employee':
        from apps.employees.models import Employee
        Employee.objects.get_or_create(user=instance)