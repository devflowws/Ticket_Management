# ticket_backend/scripts/seed_data.py
"""
Script pour remplir la base de données avec des données de test
Exécuter: python manage.py runscript seed_data
"""
from django.contrib.auth import get_user_model
from apps.employees.models import Employee, QuotaConfig
from apps.providers.models import Provider, ProviderSite
from apps.tickets.models import TicketLot, Ticket
from decimal import Decimal
from datetime import datetime, timedelta

User = get_user_model()

def run():
    print("Création des données de test...")
    
    # Configuration des quotas
    config, created = QuotaConfig.objects.get_or_create(
        defaults={
            'default_quota': 30,
            'max_quota': 50,
            'ticket_value': Decimal('1000'),
            'employee_percentage': Decimal('40'),
            'company_percentage': Decimal('60'),
            'ticket_validity_days': 90
        }
    )
    print("✓ Configuration des quotas créée")
    
    # Création des utilisateurs
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='Système',
        role='admin'
    )
    print("✓ Administrateur créé")
    
    validator = User.objects.create_user(
        username='validator',
        email='validator@example.com',
        password='validator123',
        first_name='Jean',
        last_name='Validateur',
        role='validator'
    )
    print("✓ Validateur créé")
    
    finance = User.objects.create_user(
        username='finance',
        email='finance@example.com',
        password='finance123',
        first_name='Marie',
        last_name='Finance',
        role='finance'
    )
    print("✓ Direction financière créée")
    
    # Création des employés
    employees_data = [
        {'username': 'john.doe', 'email': 'john.doe@example.com', 'first_name': 'John', 'last_name': 'Doe'},
        {'username': 'jane.smith', 'email': 'jane.smith@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
        {'username': 'pierre.martin', 'email': 'pierre.martin@example.com', 'first_name': 'Pierre', 'last_name': 'Martin'},
    ]
    
    employees = []
    for emp_data in employees_data:
        user = User.objects.create_user(
            **emp_data,
            password='employee123',
            role='employee'
        )
        employee = Employee.objects.create(
            user=user,
            department='IT',
            position='Développeur',
            monthly_ticket_quota=30
        )
        employees.append(employee)
        print(f"✓ Employé {user.get_full_name()} créé")
    
    # Création des prestataires
    provider1 = Provider.objects.create(
        name='Restaurant Le Gourmet',
        contact='contact@legourmet.com',
        phone='+228 90000000'
    )
    
    ProviderSite.objects.create(
        provider=provider1,
        name='Site Principal',
        address='123 Rue des Délices, Lomé',
        city='Lomé'
    )
    print("✓ Prestataire créé")
    
    # Création de lots de tickets
    for employee in employees:
        lot = TicketLot.objects.create(
            employee=employee,
            quantity=10,
            unit_value=config.ticket_value,
            employee_part=config.ticket_value * config.employee_percentage / 100,
            company_part=config.ticket_value * config.company_percentage / 100,
            expires_at=datetime.now() + timedelta(days=config.ticket_validity_days)
        )
        # Les tickets sont créés automatiquement par le signal
        print(f"✓ Lot de {lot.quantity} tickets créé pour {employee.user.get_full_name()}")
    
    print("\n✅ Données de test créées avec succès!")
    print("\nIdentifiants de connexion:")
    print("  Admin: admin@example.com / admin123")
    print("  Validateur: validator@example.com / validator123")
    print("  Finance: finance@example.com / finance123")
    print("  Employé: john.doe@example.com / employee123")