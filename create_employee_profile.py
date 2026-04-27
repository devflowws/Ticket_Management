import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.accounts.models import User
from apps.employees.models import Employee
from apps.companies.models import Company

# Trouver l'utilisateur connecté (le premier utilisateur)
user = User.objects.first()
print(f'User: {user.username}, Role: {user.role}')

# Créer le profil employé
employee, created = Employee.objects.get_or_create(user=user)
if created:
    print('Employee profile created')
else:
    print('Employee profile already exists')

# Assigner une entreprise si l'utilisateur n'en a pas
if not employee.company:
    company = Company.objects.first()
    if company:
        employee.company = company
        employee.save()
        print(f'Employee assigned to company: {company.name}')
    else:
        print('No company found')
else:
    print(f'Employee company: {employee.company.name}')

print(f'Employee ID: {employee.id}')
print(f'Employee Company ID: {employee.company.id if employee.company else None}')
