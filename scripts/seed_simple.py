"""
Script simplifié pour les données de test
Exécuter: python manage.py runscript seed_simple
"""
import sys
import os
import django
from django.utils import timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.employees.models import Employee, QuotaConfig
from apps.providers.models import Provider, ProviderSite
from apps.tickets.models import TicketLot

User = get_user_model()

def run():
    print("=" * 60)
    print("Création des données de test")
    print("=" * 60)
    
    # 1. Configuration des quotas
    config, created = QuotaConfig.objects.get_or_create(
        id=1,
        defaults={
            'default_quota': 30,
            'max_quota': 50,
            'ticket_value': Decimal('1000'),
            'employee_percentage': Decimal('40'),
            'company_percentage': Decimal('60'),
            'ticket_validity_days': 90
        }
    )
    print("✓ Configuration des quotas")
    
    # 2. Création des utilisateurs
    # Admin
    admin, _ = User.objects.get_or_create(
        email='admin@ticket-system.com',
        defaults={
            'username': 'admin_system',
            'password': 'pbkdf2_sha256$...',  # Sera remplacé par set_password
            'first_name': 'Admin',
            'last_name': 'Principal',
            'role': 'admin',
            'is_superuser': True,
            'is_staff': True
        }
    )
    admin.set_password('Admin123!')
    admin.save()
    print("✓ Admin créé")
    
    # Validateur
    validator, _ = User.objects.get_or_create(
        email='validator@ticket-system.com',
        defaults={
            'username': 'validator_main',
            'first_name': 'Paul',
            'last_name': 'Validateur',
            'role': 'validator'
        }
    )
    validator.set_password('Validator123!')
    validator.save()
    print("✓ Validateur créé")
    
    # Finance
    finance, _ = User.objects.get_or_create(
        email='finance@ticket-system.com',
        defaults={
            'username': 'finance_dir',
            'first_name': 'Claire',
            'last_name': 'Dubois',
            'role': 'finance'
        }
    )
    finance.set_password('Finance123!')
    finance.save()
    print("✓ Direction financière créée")
    
    # 3. Employés
    employees_data = [
        {'email': 'emma.laurent@entreprise.com', 'first_name': 'Emma', 'last_name': 'Laurent', 'dept': 'Marketing'},
        {'email': 'thomas.bernard@entreprise.com', 'first_name': 'Thomas', 'last_name': 'Bernard', 'dept': 'IT'},
        {'email': 'sophie.martin@entreprise.com', 'first_name': 'Sophie', 'last_name': 'Martin', 'dept': 'RH'},
    ]
    
    employees = []
    for emp_data in employees_data:
        user, _ = User.objects.get_or_create(
            email=emp_data['email'],
            defaults={
                'username': emp_data['email'].split('@')[0],
                'first_name': emp_data['first_name'],
                'last_name': emp_data['last_name'],
                'role': 'employee'
            }
        )
        user.set_password('Employee123!')
        user.save()
        
        employee, _ = Employee.objects.get_or_create(
            user=user,
            defaults={
                'department': emp_data['dept'],
                'position': 'Employé',
                'monthly_ticket_quota': 30
            }
        )
        employees.append(employee)
        print(f"✓ Employé: {user.get_full_name()}")
    
    # 4. Prestataires
    provider1, _ = Provider.objects.get_or_create(
        name='Restaurant Le Gourmet',
        defaults={
            'contact': 'contact@legourmet.com',
            'phone': '+228 90210001',
            'is_active': True
        }
    )
    
    ProviderSite.objects.get_or_create(
        provider=provider1,
        name='Site Lomé Centre',
        defaults={
            'address': '123 Boulevard du 13 Janvier',
            'city': 'Lomé'
        }
    )
    print("✓ Prestataires créés")
    
    # 5. Lots de tickets
    for employee in employees:
        lot, _ = TicketLot.objects.get_or_create(
            employee=employee,
            quantity=10,
            defaults={
                'unit_value': config.ticket_value,
                'employee_part': config.ticket_value * config.employee_percentage / 100,
                'company_part': config.ticket_value * config.company_percentage / 100,
                'expires_at': timezone.now() + timezone.timedelta(days=config.ticket_validity_days)
            }
        )
        print(f"✓ Lot tickets: {employee.user.get_full_name()} - {lot.quantity} tickets")
    
    print("\n" + "=" * 60)
    print("COMPTES DE TEST")
    print("=" * 60)
    print("Admin: admin@ticket-system.com / Admin123!")
    print("Validateur: validator@ticket-system.com / Validator123!")
    print("Finance: finance@ticket-system.com / Finance123!")
    print("Employés: emma.laurent@entreprise.com / Employee123!")
    print("\n✅ Données créées avec succès!")