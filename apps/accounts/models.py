# ticket_backend/apps/accounts/models.py
"""
Modèles pour la gestion des utilisateurs et authentification
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    """Choix des rôles utilisateurs"""
    ADMIN = 'admin', _('Administrateur')
    EMPLOYEE = 'employee', _('Employé')
    VALIDATOR = 'validator', _('Responsable validation')
    FINANCE = 'finance', _('Direction financière')


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec gestion des rôles
    """
    ROLE_CHOICES = [
        (Role.ADMIN, 'Administrateur'),
        (Role.EMPLOYEE, 'Employé'),
        (Role.VALIDATOR, 'Responsable validation'),
        (Role.FINANCE, 'Direction financière'),
    ]
    
    email = models.EmailField(_('adresse email'), unique=True)
    role = models.CharField(
        _('rôle'),
        max_length=20,
        choices=ROLE_CHOICES,
        default=Role.EMPLOYEE
    )
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    is_active = models.BooleanField(_('actif'), default=True)
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    # Nouveaux champs pour la gestion d'entreprise
    company_name = models.CharField(_('nom de l\'entreprise'), max_length=200, blank=True)
    company_tax_id = models.CharField(_('numéro fiscal'), max_length=50, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == Role.ADMIN
    
    @property
    def is_employee(self):
        return self.role == Role.EMPLOYEE
    
    @property
    def is_validator(self):
        return self.role == Role.VALIDATOR
    
    @property
    def is_finance(self):
        return self.role == Role.FINANCE