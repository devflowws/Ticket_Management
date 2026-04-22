# apps/consumption_requests/apps.py
from django.apps import AppConfig


class ConsumptionRequestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.consumption_requests'
    verbose_name = 'Demandes de consommation'