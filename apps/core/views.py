# apps/core/views.py - Version complète
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.employees.models import Employee, QuotaConfig
from apps.providers.models import Provider
from apps.tickets.models import Ticket, EmployeeBalance
from apps.purchases.models import PurchaseRequest


def landing_page(request):
    """Page d'accueil publique"""
    return render(request, 'landing/index.html')


def register_company(request):
    """Inscription d'une nouvelle entreprise"""
    if request.method == 'POST':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        company_name = request.POST.get('company_name')
        admin_email = request.POST.get('admin_email')
        admin_password = request.POST.get('password')
        
        # Créer l'admin
        admin = User.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=admin_password,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            role='admin',
            company_name=company_name
        )
        
        # Configurer les quotas
        QuotaConfig.objects.create(
            ticket_value=request.POST.get('ticket_value', 1000),
            employee_percentage=request.POST.get('employee_percentage', 40),
            company_percentage=100 - float(request.POST.get('employee_percentage', 40)),
            default_quota=request.POST.get('default_quota', 30),
            ticket_validity_days=request.POST.get('ticket_validity_days', 90)
        )
        
        messages.success(request, 'Entreprise créée avec succès ! Connectez-vous.')
        return redirect('login')
    
    return render(request, 'accounts/register_company.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user:
            login(request, user)
            messages.success(request, f'Bienvenue {user.get_full_name()} !')
            
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'employee':
                return redirect('employee_dashboard')
            elif user.role == 'validator':
                return redirect('validator_dashboard')
            elif user.role == 'finance':
                return redirect('finance_dashboard')
        else:
            messages.error(request, 'Email ou mot de passe incorrect')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté')
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if request.user.check_password(old_password):
            if new_password1 == new_password2:
                request.user.set_password(new_password1)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Mot de passe modifié avec succès')
                return redirect('profile')
            else:
                messages.error(request, 'Les nouveaux mots de passe ne correspondent pas')
        else:
            messages.error(request, 'Mot de passe actuel incorrect')
    
    return render(request, 'accounts/change_password.html')


@login_required
def admin_dashboard(request):
    context = {
        'employees_count': Employee.objects.count(),
        'providers_count': Provider.objects.count(),
        'active_tickets': Ticket.objects.filter(status='active').count(),
        'pending_requests': PurchaseRequest.objects.filter(status='pending').count(),
        'months': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
        'purchases_data': [12, 19, 25, 32, 28, 35, 42, 38, 45, 52, 48, 55],
        'provider_names': ['Resto A', 'Resto B', 'Resto C', 'Resto D'],
        'consumptions_data': [1250, 980, 720, 540],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def employee_dashboard(request):
    employee = request.user.employee_profile
    balance = EmployeeBalance.objects.filter(employee=employee).first()
    context = {
        'employee': employee,
        'balance': balance.active_tickets if balance else 0,
        'pending_purchases': PurchaseRequest.objects.filter(employee=employee, status='pending').count(),
    }
    return render(request, 'dashboard/employee_dashboard.html', context)


@login_required
def validator_dashboard(request):
    context = {
        'pending_requests': PurchaseRequest.objects.filter(status='pending').count(),
        'total_validated': PurchaseRequest.objects.filter(status='approved').count(),
    }
    return render(request, 'dashboard/validator_dashboard.html', context)


@login_required
def finance_dashboard(request):
    context = {
        'total_tickets_sold': Ticket.objects.filter(status='used').count(),
    }
    return render(request, 'dashboard/finance_dashboard.html', context)


# Vues supplémentaires pour les URLs
@login_required
def my_balance(request):
    return render(request, 'tickets/balance.html')


@login_required
def purchase_request_create(request):
    return render(request, 'purchases/create.html')


@login_required
def my_orders(request):
    return render(request, 'orders/list.html')


@login_required
def pending_validations(request):
    return render(request, 'validations/pending.html')


@login_required
def validation_history(request):
    return render(request, 'validations/history.html')


@login_required
def reports_dashboard(request):
    return render(request, 'reports/dashboard.html')


@login_required
def provider_payment(request):
    return render(request, 'reports/provider_payment.html')


@login_required
def provider_list(request):
    return render(request, 'providers/list.html')


@login_required
def menu_list(request):
    return render(request, 'menus/list.html')



def landing_page(request):
    """Page d'accueil publique"""
    return render(request, 'landing/index.html')