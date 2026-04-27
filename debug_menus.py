from apps.menus.models import DailyMenu, Menu
from apps.providers.models import Provider
from apps.companies.models import Company
from apps.employees.models import Employee
from datetime import datetime

print('=== DAILY MENUS ===')
menus = DailyMenu.objects.all()
print(f'Total DailyMenu: {menus.count()}')
for m in menus:
    print(f'ID: {m.id}, Title: {m.title}, Date: {m.date}, Available: {m.is_available}, Provider: {m.provider.name}, Provider Company: {m.provider.company.name if m.provider.company else None}')

print('\n=== MENU ===')
menus2 = Menu.objects.all()
print(f'Total Menu: {menus2.count()}')
for m in menus2:
    print(f'ID: {m.id}, Name: {m.name}, Available: {m.is_available}, Provider: {m.provider.name}, Provider Company: {m.provider.company.name if m.provider.company else None}')

print('\n=== PROVIDERS ===')
providers = Provider.objects.all()
print(f'Total Provider: {providers.count()}')
for p in providers:
    print(f'ID: {p.id}, Name: {p.name}, Company: {p.company.name if p.company else None}')

print('\n=== EMPLOYEES ===')
employees = Employee.objects.all()
print(f'Total Employee: {employees.count()}')
for e in employees:
    print(f'ID: {e.id}, User: {e.user.username}, Company: {e.company.name if e.company else None}')

print('\n=== COMPANIES ===')
companies = Company.objects.all()
print(f'Total Company: {companies.count()}')
for c in companies:
    print(f'ID: {c.id}, Name: {c.name}')
