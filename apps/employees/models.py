# ticket_backend/apps/employees/models.py
"""
Modèles pour la gestion des employés
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User


class Employee(models.Model):
    """
    Profil employé avec informations spécifiques
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='employee_profile',
        verbose_name=_('utilisateur')
    )
    department = models.CharField(_('département'), max_length=100, blank=True)
    position = models.CharField(_('poste'), max_length=100, blank=True)
    phone = models.CharField(_('téléphone professionnel'), max_length=20, blank=True)
    hire_date = models.DateField(_('date d\'embauche'), null=True, blank=True)
    
    # Champs pour la gestion des tickets
    monthly_ticket_quota = models.PositiveIntegerField(
        _('quota mensuel de tickets'),
        default=30,
        help_text=_('Nombre maximum de tickets que l\'employé peut obtenir par mois')
    )
    current_month_tickets = models.PositiveIntegerField(
        _('tickets achetés ce mois'),
        default=0,
        help_text=_('Nombre de tickets achetés dans le mois en cours')
    )
    last_quota_reset = models.DateField(
        _('dernier reset du quota'),
        auto_now_add=True,
        help_text=_('Date du dernier réinitialisation du quota mensuel')
    )
    
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('employé')
        verbose_name_plural = _('employés')
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return self.user.get_full_name()
    
    @property
    def remaining_quota(self):
        """Calcule le quota restant pour le mois"""
        return max(0, self.monthly_ticket_quota - self.current_month_tickets)
    
    @property
    def can_request_tickets(self, quantity=1):
        """Vérifie si l'employé peut demander des tickets"""
        return self.remaining_quota >= quantity
    
    def reset_monthly_quota_if_needed(self):
        """Réinitialise le quota mensuel si nécessaire"""
        from django.utils import timezone
        today = timezone.now().date()
        
        # Si le dernier reset n'est pas dans le même mois
        if self.last_quota_reset.month != today.month or \
           self.last_quota_reset.year != today.year:
            self.current_month_tickets = 0
            self.last_quota_reset = today
            self.save(update_fields=['current_month_tickets', 'last_quota_reset'])


class QuotaConfig(models.Model):
    """
    Configuration globale des quotas
    """
    default_quota = models.PositiveIntegerField(
        _('quota par défaut'),
        default=30,
        help_text=_('Quota mensuel par défaut pour les nouveaux employés')
    )
    max_quota = models.PositiveIntegerField(
        _('quota maximum'),
        default=50,
        help_text=_('Quota mensuel maximum autorisé')
    )
    ticket_value = models.DecimalField(
        _('valeur du ticket'),
        max_digits=10,
        decimal_places=2,
        default=1000,
        help_text=_('Valeur monétaire d\'un ticket en FCFA')
    )
    employee_percentage = models.DecimalField(
        _('part employé (%)'),
        max_digits=5,
        decimal_places=2,
        default=40,
        help_text=_('Pourcentage du ticket payé par l\'employé')
    )
    company_percentage = models.DecimalField(
        _('part entreprise (%)'),
        max_digits=5,
        decimal_places=2,
        default=60,
        help_text=_('Pourcentage du ticket payé par l\'entreprise')
    )
    ticket_validity_days = models.PositiveIntegerField(
        _('validité des tickets (jours)'),
        default=90,
        help_text=_('Nombre de jours de validité des tickets après achat')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('configuration des quotas')
        verbose_name_plural = _('configurations des quotas')
    
    def __str__(self):
        return f"Quota: {self.default_quota} tickets - Valeur: {self.ticket_value} FCFA"
    
    def save(self, *args, **kwargs):
        # Assure qu'il n'y a qu'une seule configuration active
        if not self.pk and QuotaConfig.objects.exists():
            raise ValueError("Une configuration existe déjà. Utilisez modify pour la mettre à jour.")
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_config(cls):
        """Récupère la configuration active"""
        config = cls.objects.first()
        if not config:
            config = cls.objects.create()
        return config