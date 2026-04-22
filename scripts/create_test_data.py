# ticket_backend/scripts/create_test_data.py
"""
Script pour créer des données de test complètes
Exécuter: python manage.py runscript create_test_data
"""
import sys
import os
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from apps.employees.models import Employee, QuotaConfig
from apps.providers.models import Provider, ProviderSite
from apps.tickets.models import TicketLot
from apps.menus.models import DailyMenu

User = get_user_model()

def run():
    print("=" * 60)
    print("Création des données de test complètes")
    print("=" * 60)
    
    # 1. Configuration
    config, _ = QuotaConfig.objects.update_or_create(
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
    print("✓ Configuration: OK")
    
    # 2. Création des utilisateurs par rôle
    users = {
        'admin': User.objects.create_superuser(
            username='admin_system',
            email='admin@ticket-system.com',
            password='Admin123!',
            first_name='Admin',
            last_name='Principal',
            role='admin'
        ),
        'validator': User.objects.create_user(
            username='validator_main',
            email='validator@ticket-system.com',
            password='Validator123!',
            first_name='Paul',
            last_name='Validateur',
            role='validator'
        ),
        'finance': User.objects.create_user(
            username='finance_dir',
            email='finance@ticket-system.com',
            password='Finance123!',
            first_name='Claire',
            last_name='Dubois',
            role='finance'
        ),
    }
    print("✓ Utilisateurs système créés")
    
    # 3. Création des employés
    employees_list = [
        {'username': 'emma.laurent', 'email': 'emma.laurent@entreprise.com', 
         'first_name': 'Emma', 'last_name': 'Laurent', 'dept': 'Marketing', 'position': 'Chef de projet'},
        {'username': 'thomas.bernard', 'email': 'thomas.bernard@entreprise.com', 
         'first_name': 'Thomas', 'last_name': 'Bernard', 'dept': 'IT', 'position': 'Développeur Senior'},
        {'username': 'sophie.martin', 'email': 'sophie.martin@entreprise.com', 
         'first_name': 'Sophie', 'last_name': 'Martin', 'dept': 'RH', 'position': 'Responsable RH'},
        {'username': 'lucas.petit', 'email': 'lucas.petit@entreprise.com', 
         'first_name': 'Lucas', 'last_name': 'Petit', 'dept': 'Finance', 'position': 'Analyste'},
        {'username': 'julie.rousseau', 'email': 'julie.rousseau@entreprise.com', 
         'first_name': 'Julie', 'last_name': 'Rousseau', 'dept': 'Commercial', 'position': 'Commerciale'},
    ]
    
    employees = []
    for emp_data in employees_list:
        user = User.objects.create_user(
            username=emp_data['username'],
            email=emp_data['email'],
            password='Employee123!',
            first_name=emp_data['first_name'],
            last_name=emp_data['last_name'],
            role='employee'
        )
        employee = Employee.objects.create(
            user=user,
            department=emp_data['dept'],
            position=emp_data['position'],
            monthly_ticket_quota=30,
            current_month_tickets=0
        )
        employees.append(employee)
        print(f"✓ Employé: {user.get_full_name()} - {emp_data['dept']}")
    
    # 4. Création des prestataires
    providers_data = [
        {'name': 'Restaurant Le Gourmet', 'contact': 'contact@legourmet.com', 
         'phone': '+228 90210001', 'sites': [
             {'name': 'Site Lomé Centre', 'address': '123 Boulevard du 13 Janvier', 'city': 'Lomé'},
             {'name': 'Site Lomé Plage', 'address': '45 Rue des Lacs', 'city': 'Lomé'}
         ]},
        {'name': 'Pizzeria Bella Italia', 'contact': 'info@bellatialomé.com', 
         'phone': '+228 90210002', 'sites': [
             {'name': 'Site Principal', 'address': '78 Avenue de la Renaissance', 'city': 'Lomé'}
         ]},
        {'name': 'Café de Paris', 'contact': 'contact@cafedeparis.com', 
         'phone': '+228 90210003', 'sites': [
             {'name': 'Site Hedzranawoé', 'address': '12 Rue des Accras', 'city': 'Lomé'}
         ]},
    ]
    
    providers = []
    for prov_data in providers_data:
        provider = Provider.objects.create(
            name=prov_data['name'],
            contact=prov_data['contact'],
            phone=prov_data['phone']
        )
        for site_data in prov_data['sites']:
            ProviderSite.objects.create(
                provider=provider,
                name=site_data['name'],
                address=site_data['address'],
                city=site_data['city']
            )
        providers.append(provider)
        print(f"✓ Prestataire: {provider.name} - {provider.sites.count()} site(s)")
    
    # 5. Création des lots de tickets pour chaque employé
    for employee in employees:
        lot = TicketLot.objects.create(
            employee=employee,
            quantity=25,
            unit_value=config.ticket_value,
            employee_part=config.ticket_value * config.employee_percentage / 100,
            company_part=config.ticket_value * config.company_percentage / 100,
            expires_at=timezone.now() + timedelta(days=config.ticket_validity_days)
        )
        print(f"✓ Lot tickets créé: {employee.user.get_full_name()} - {lot.quantity} tickets")
    
    # 6. Création des menus
    today = timezone.now().date()
    menus = [
        {'date': today, 'title': 'Menu du jour', 'description': 'Plat du jour + Dessert + Boisson', 'deadline_hour': 10},
        {'date': today + timedelta(days=1), 'title': 'Menu Poisson', 'description': 'Poisson grillé + Riz + Légumes', 'deadline_hour': 10},
        {'date': today + timedelta(days=2), 'title': 'Menu Burger', 'description': 'Burger maison + Frites + Boisson', 'deadline_hour': 10},
    ]
    
    for menu_data in menus:
        menu, created = DailyMenu.objects.get_or_create(
            date=menu_data['date'],
            defaults={
                'title': menu_data['title'],
                'description': menu_data['description'],
                'deadline_hour': menu_data['deadline_hour']
            }
        )
        print(f"✓ Menu: {menu.title} - {menu.date}")
    
    # 7. Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES DONNÉES CRÉÉES")
    print("=" * 60)
    print(f"👥 Utilisateurs: {User.objects.count()}")
    print(f"👔 Employés: {Employee.objects.count()}")
    print(f"🏢 Prestataires: {Provider.objects.count()}")
    print(f"🏪 Sites prestataires: {ProviderSite.objects.count()}")
    print(f"🎫 Lots tickets: {TicketLot.objects.count()}")
    print(f"📅 Menus: {DailyMenu.objects.count()}")
    
    print("\n" + "=" * 60)
    print("COMPTES DE TEST")
    print("=" * 60)
    print("🔐 ADMINISTRATEUR")
    print("   Email: admin@ticket-system.com")
    print("   Mot de passe: Admin123!")
    print("\n✅ VALIDATEUR")
    print("   Email: validator@ticket-system.com")
    print("   Mot de passe: Validator123!")
    print("\n💰 DIRECTION FINANCIÈRE")
    print("   Email: finance@ticket-system.com")
    print("   Mot de passe: Finance123!")
    print("\n👔 EMPLOYÉS")
    for emp in employees:
        print(f"   {emp.user.email} / Employee123!")
    
    print("\n" + "=" * 60)
    print("🔗 ACCÈS SWAGGER")
    print("=" * 60)
    print("Documentation interactive:")
    print("  → http://localhost:8000/swagger/")
    print("\nInterface ReDoc:")
    print("  → http://localhost:8000/redoc/")
    print("\n" + "=" * 60)
    print("✅ Données de test créées avec succès!")