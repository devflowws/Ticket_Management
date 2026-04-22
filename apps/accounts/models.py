# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# Import correct - sans "ticket_backend."
from apps.companies.models import Company


class Role(models.TextChoices):
    ADMIN = 'admin', _('Administrateur')
    EMPLOYEE = 'employee', _('Employé')
    VALIDATOR = 'validator', _('Responsable validation')
    FINANCE = 'finance', _('Direction financière')
    PROVIDER = 'provider', _('Prestataire')


class User(AbstractUser):
    email = models.EmailField(_('adresse email'), unique=True)
    role = models.CharField(_('rôle'), max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    is_active = models.BooleanField(_('actif'), default=True)
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    # Company relation - temporairement commentée car companies n'existe pas encore
    # company = models.ForeignKey(
    #     Company, 
    #     on_delete=models.CASCADE, 
    #     related_name='users',
    #     null=True, 
    #     blank=True
    # )
    
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
    
    @property
    def is_provider(self):
        return self.role == Role.PROVIDER