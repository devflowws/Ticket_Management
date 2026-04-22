# apps/reporting/models.py
from django.db import models
from django.utils import timezone


class ReportCache(models.Model):
    """Cache pour les rapports pré-calculés"""
    REPORT_TYPES = [
        ('monthly', 'Rapport mensuel'),
        ('provider', 'Rapport prestataire'),
        ('employee', 'Rapport employé'),
        ('financial', 'Rapport financier'),
    ]
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    period = models.CharField(max_length=20, help_text="Mois ou année concerné")
    data = models.JSONField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['report_type', 'period']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.period}"