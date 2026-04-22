# ticket_backend/apps/employees/apps.py
from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.employees'
    verbose_name = 'Gestion des employés'
    
    def ready(self):
        import apps.employees.signals