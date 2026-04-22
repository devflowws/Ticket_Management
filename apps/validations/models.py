# apps/validations/models.py
"""
Modèles pour le workflow de validation
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.purchases.models import PurchaseRequest
from apps.accounts.models import User


class ValidationLog(models.Model):
    """Journal des validations"""
    
    class Decision(models.TextChoices):
        APPROVED = 'approved', _('Approuvé')
        REFUSED = 'refused', _('Refusé')
    
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='validation_logs',
        verbose_name=_('demande d\'achat')
    )
    validator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='validation_logs',
        verbose_name=_('validateur')
    )
    decision = models.CharField(
        _('décision'),
        max_length=20,
        choices=Decision.choices
    )
    comment = models.TextField(_('commentaire'), blank=True)
    created_at = models.DateTimeField(_('date de décision'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('journal de validation')
        verbose_name_plural = _('journaux de validation')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.purchase_request} - {self.get_decision_display()} par {self.validator}"