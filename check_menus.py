import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.menus.models import DailyMenu, Menu
from apps.providers.models import Provider
from apps.companies.models import Company
from apps.employees.models import Employee
from datetime import datetime, timedelta

print("=== VÉRIFICATION DES DONNÉES ===")

# Vérifier les entreprises
companies = Company.objects.all()
print(f"Entreprises trouvées: {companies.count()}")
for c in companies:
    print(f"  - {c.name} (ID: {c.id})")

# Vérifier les prestataires
providers = Provider.objects.all()
print(f"\nPrestataires trouvés: {providers.count()}")
for p in providers:
    print(f"  - {p.name} (ID: {p.id}), Entreprise: {p.company.name if p.company else 'None'}")

# Vérifier les DailyMenu
daily_menus = DailyMenu.objects.all()
print(f"\nDailyMenus trouvés: {daily_menus.count()}")
for dm in daily_menus:
    print(f"  - {dm.title} (ID: {dm.id}), Date: {dm.date}, Disponible: {dm.is_available}, Prestataire: {dm.provider.name}")

# Vérifier les Menu (autres menus)
menus = Menu.objects.all()
print(f"\nMenus (autres) trouvés: {menus.count()}")
for m in menus:
    print(f"  - {m.name} (ID: {m.id}), Disponible: {m.is_available}, Prestataire: {m.provider.name}")

# Vérifier les employés
employees = Employee.objects.all()
print(f"\nEmployés trouvés: {employees.count()}")
for e in employees:
    print(f"  - {e.user.username} (ID: {e.id}), Entreprise: {e.company.name if e.company else 'None'}")

print("\n=== FIN VÉRIFICATION ===")
