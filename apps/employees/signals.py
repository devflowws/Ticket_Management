# ticket_backend/apps/employees/signals.py
"""
Signaux pour l'application employees
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Employee, QuotaConfig


@receiver(pre_save, sender=Employee)
def reset_quota_if_needed(sender, instance, **kwargs):
    """Réinitialise le quota avant sauvegarde si nécessaire"""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            # Vérifie si le mois a changé
            if (old_instance.last_quota_reset.month != timezone.now().date().month or
                old_instance.last_quota_reset.year != timezone.now().date().year):
                instance.current_month_tickets = 0
                instance.last_quota_reset = timezone.now().date()
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender=Employee)
def apply_default_quota(sender, instance, created, **kwargs):
    """Applique le quota par défaut lors de la création"""
    if created:
        config = QuotaConfig.get_active_config()
        instance.monthly_ticket_quota = config.default_quota
        instance.save(update_fields=['monthly_ticket_quota'])