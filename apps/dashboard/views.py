# apps/dashboard/views.py - Ajouter ces fonctions
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.employees.models import Employee
from apps.providers.models import Provider
from apps.purchases.models import PurchaseRequest
from apps.tickets.models import Ticket


@login_required
def admin_dashboard(request):
    context = {
        'user': request.user,
        'employees_count': Employee.objects.count(),
        'providers_count': Provider.objects.count(),
        'active_tickets': Ticket.objects.filter(status='active').count(),
        'pending_requests': PurchaseRequest.objects.filter(status='pending').count(),
        'months': ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin'],
        'purchases_data': [10, 25, 30, 45, 60, 55],
        'provider_names': ['Resto A', 'Resto B', 'Resto C'],
        'consumptions_data': [120, 80, 45],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def employee_dashboard(request):
    employee = request.user.employee_profile
    context = {
        'user': request.user,
        'employee': employee,
        'balance': employee.balance.active_tickets if hasattr(employee, 'balance') else 0,
        'pending_purchases': PurchaseRequest.objects.filter(employee=employee, status='pending').count(),
    }
    return render(request, 'dashboard/employee_dashboard.html', context)


@login_required
def validator_dashboard(request):
    context = {
        'user': request.user,
        'pending_requests': PurchaseRequest.objects.filter(status='pending').count(),
        'total_validated': PurchaseRequest.objects.filter(status='approved').count(),
        'pending_list': PurchaseRequest.objects.filter(status='pending')[:10]
    }
    return render(request, 'dashboard/validator_dashboard.html', context)


@login_required
def finance_dashboard(request):
    context = {
        'user': request.user,
        'total_tickets_sold': Ticket.objects.filter(status='used').count(),
    }
    return render(request, 'dashboard/finance_dashboard.html', context)


# Alias pour éviter les erreurs
dashboard = admin_dashboard