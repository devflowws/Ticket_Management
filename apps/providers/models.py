# apps/providers/models.py
"""
Modèles pour la gestion des prestataires
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class Provider(models.Model):
    """Prestataire (restaurant, fournisseur, etc.)"""
    
    # Informations générales
    name = models.CharField(_('nom'), max_length=200)
    commercial_name = models.CharField(_('nom commercial'), max_length=200, blank=True)
    registration_number = models.CharField(_('numéro d\'enregistrement'), max_length=100, blank=True)
    tax_id = models.CharField(_('numéro fiscal'), max_length=100, blank=True)
    
    # Contact
    contact_person = models.CharField(_('personne de contact'), max_length=200, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('téléphone'), max_length=50, blank=True, default='')  # Ajouter blank=True, default=''
    alternative_phone = models.CharField(_('téléphone alternatif'), max_length=50, blank=True)
    
    # Adresse
    address = models.TextField(_('adresse'), blank=True, default='')  # Ajouter blank=True, default=''
    city = models.CharField(_('ville'), max_length=100, blank=True, default='')  # Ajouter blank=True, default=''
    country = models.CharField(_('pays'), max_length=100, default='Togo')
    postal_code = models.CharField(_('code postal'), max_length=20, blank=True)
    
    # Modes de paiement acceptés
    PAYMENT_METHODS = [
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Virement bancaire'),
        ('check', 'Chèque'),
        ('cash', 'Espèces'),
        ('card', 'Carte bancaire'),
    ]
    payment_methods = models.JSONField(_('modes de paiement'), default=list, blank=True)
    
    # Contrat
    contract_number = models.CharField(_('numéro de contrat'), max_length=100, blank=True)
    contract_start = models.DateField(_('début contrat'), null=True, blank=True)
    contract_end = models.DateField(_('fin contrat'), null=True, blank=True)
    contract_file = models.FileField(_('fichier contrat'), upload_to='contracts/%Y/%m/', null=True, blank=True)
    
    # Notes et évaluation
    notes = models.TextField(_('notes'), blank=True)
    rating = models.DecimalField(_('note'), max_digits=3, decimal_places=2, default=0, help_text='Note sur 5')
    
    # Statut
    is_active = models.BooleanField(_('actif'), default=True)
    is_preferred = models.BooleanField(_('partenaire privilégié'), default=False)
    
    # Finances
    total_tickets_sold = models.PositiveIntegerField(_('total tickets vendus'), default=0)
    total_amount_due = models.DecimalField(_('total dû'), max_digits=12, decimal_places=2, default=0)
    total_amount_paid = models.DecimalField(_('total payé'), max_digits=12, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('date création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date modification'), auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='providers_created')
    
    class Meta:
        verbose_name = _('prestataire')
        verbose_name_plural = _('prestataires')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['city']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def balance(self):
        """Solde dû au prestataire"""
        return self.total_amount_due - self.total_amount_paid
    
    @property
    def display_name(self):
        return self.commercial_name or self.name
    
    def update_financials(self):
        """Met à jour les totaux financiers"""
        from apps.consumption.models import Consumption
        
        consumptions = Consumption.objects.filter(provider=self, status='confirmed')
        self.total_tickets_sold = consumptions.aggregate(total=models.Sum('nb_tickets'))['total'] or 0
        self.total_amount_due = consumptions.aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0')
        self.save(update_fields=['total_tickets_sold', 'total_amount_due'])


class ProviderSite(models.Model):
    """Site d'un prestataire (localisation géographique)"""
    
    provider = models.ForeignKey(
        Provider, 
        on_delete=models.CASCADE, 
        related_name='sites',
        verbose_name=_('prestataire')
    )
    name = models.CharField(_('nom du site'), max_length=200)
    code = models.CharField(_('code du site'), max_length=50, unique=True, blank=True)
    
    # Localisation
    address = models.TextField(_('adresse'))
    city = models.CharField(_('ville'), max_length=100)
    district = models.CharField(_('quartier'), max_length=100, blank=True)
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Contact spécifique au site
    phone = models.CharField(_('téléphone'), max_length=50, blank=True)
    manager_name = models.CharField(_('nom du responsable'), max_length=200, blank=True)
    manager_phone = models.CharField(_('téléphone du responsable'), max_length=50, blank=True)
    
    # Horaires d'ouverture (stocké en JSON)
    opening_hours = models.JSONField(_('horaires d\'ouverture'), default=dict, blank=True)
    # Exemple: {"monday": "08:00-17:00", "tuesday": "08:00-17:00", ...}
    
    # Capacité
    capacity = models.PositiveIntegerField(_('capacité (couverts)'), default=0)
    
    is_active = models.BooleanField(_('actif'), default=True)
    is_main_site = models.BooleanField(_('site principal'), default=False)
    
    created_at = models.DateTimeField(_('date création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('site prestataire')
        verbose_name_plural = _('sites prestataires')
        ordering = ['provider__name', 'name']
        unique_together = [['provider', 'code']]
    
    def __str__(self):
        return f"{self.provider.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.code:
            # Générer un code unique
            import uuid
            self.code = f"{self.provider.id}_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class ProviderCategory(models.Model):
    """Catégorie de prestataire (Restaurant, Traiteur, etc.)"""
    name = models.CharField(_('nom'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icône'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('catégorie')
        verbose_name_plural = _('catégories')
    
    def __str__(self):
        return self.name