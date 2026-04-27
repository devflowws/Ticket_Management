# apps/core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.employees.models import Employee
from apps.providers.models import Provider
from apps.tickets.models import Ticket, EmployeeBalance
from apps.purchases.models import PurchaseRequest
from apps.companies.models import Company
from apps.tickets.models import Ticket, TicketLot, EmployeeBalance


def landing_page(request):
    """Page d'accueil publique"""
    return render(request, 'landing/index.html')


def register_company(request):
    """Inscription d'une nouvelle entreprise"""
    if request.method == 'POST':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Récupérer les données du formulaire
        company_name = request.POST.get('company_name')
        company_email = request.POST.get('company_email')
        company_phone = request.POST.get('phone')
        company_address = request.POST.get('address')
        company_city = request.POST.get('city')
        company_country = request.POST.get('country', 'Togo')
        
        # Données admin
        admin_first_name = request.POST.get('first_name')
        admin_last_name = request.POST.get('last_name')
        admin_email = request.POST.get('admin_email')
        admin_password = request.POST.get('password')
        
        # Configuration des tickets
        ticket_value = request.POST.get('ticket_value', 1000)
        employee_percentage = float(request.POST.get('employee_percentage', 40))
        default_quota = request.POST.get('default_quota', 30)
        ticket_validity_days = request.POST.get('ticket_validity_days', 90)
        
        # 1. Créer l'entreprise
        company = Company.objects.create(
            name=company_name,
            email=company_email,
            phone=company_phone,
            address=company_address,
            city=company_city,
            country=company_country,
            ticket_value=ticket_value,
            employee_percentage=employee_percentage,
            company_percentage=100 - employee_percentage,
            default_quota=default_quota,
            ticket_validity_days=ticket_validity_days,
            is_active=True
        )
        
        # 2. Créer l'utilisateur admin
        admin = User.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=admin_password,
            first_name=admin_first_name,
            last_name=admin_last_name,
            role='admin'
        )
        
        # Lier l'admin à l'entreprise
        try:
            admin.company = company
            admin.save()
        except:
            pass
        
        messages.success(request, f'Entreprise "{company_name}" créée avec succès ! Connectez-vous.')
        return redirect('login')
    
    return render(request, 'accounts/register_company.html')


def login_view(request):
    """Connexion pour le web"""
    from apps.companies.models import Company
    
    companies = Company.objects.filter(is_active=True)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user:
            login(request, user)
            messages.success(request, f'Bienvenue {user.get_full_name()} !')
            
            # Redirection selon le rôle
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'employee':
                return redirect('employee_dashboard')
            elif user.role == 'validator':
                return redirect('validator_dashboard')
            elif user.role == 'finance':
                return redirect('finance_dashboard')
            elif user.role == 'provider':
                return redirect('provider_dashboard')
        else:
            messages.error(request, 'Email ou mot de passe incorrect')
    
    return render(request, 'accounts/login.html', {'companies': companies})
    """Connexion avec sélection du rôle"""
    from apps.companies.models import Company
    
    # Récupérer toutes les entreprises actives
    companies = Company.objects.filter(is_active=True)
    
    # Debug - afficher dans le terminal
    print(f"=== PAGE DE CONNEXION ===")
    print(f"Nombre d'entreprises: {companies.count()}")
    for c in companies:
        print(f"  - {c.name} (ID: {c.id})")
    
    if request.method == 'POST':
        role = request.POST.get('role')
        email = request.POST.get('email')
        password = request.POST.get('password')
        company_id = request.POST.get('company_id')
        
        print(f"Tentative connexion - Rôle: {role}, Email: {email}, Company ID: {company_id}")
        
        user = authenticate(request, username=email, password=password)
        
        if user:
            print(f"Utilisateur trouvé: {user.email}, Rôle réel: {user.role}")
            
            # Vérifier que le rôle correspond
            if user.role != role:
                messages.error(request, f'Ce compte n\'est pas un compte {role}. Veuillez sélectionner le bon rôle.')
                return render(request, 'accounts/login.html', {'companies': companies})
            
            # Pour les non-admin, vérifier l'entreprise
            if role != 'admin':
                if not company_id:
                    messages.error(request, 'Veuillez sélectionner votre entreprise')
                    return render(request, 'accounts/login.html', {'companies': companies})
                
                try:
                    company = Company.objects.get(id=company_id)
                    # Vérifier que l'utilisateur appartient à cette entreprise
                    if user.company and user.company.id != company.id:
                        messages.error(request, f'Vous n\'êtes pas autorisé à accéder à l\'entreprise "{company.name}"')
                        return render(request, 'accounts/login.html', {'companies': companies})
                except Company.DoesNotExist:
                    messages.error(request, 'Entreprise non trouvée')
                    return render(request, 'accounts/login.html', {'companies': companies})
            
            login(request, user)
            request.session['current_company_id'] = int(company_id) if company_id else None
            messages.success(request, f'Bienvenue {user.get_full_name()} !')
            
            # Redirection selon le rôle
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'employee':
                return redirect('employee_dashboard')
            elif user.role == 'validator':
                return redirect('validator_dashboard')
            elif user.role == 'finance':
                return redirect('finance_dashboard')
            elif user.role == 'provider':
                return redirect('provider_dashboard')
        else:
            messages.error(request, 'Email ou mot de passe incorrect')
    
    return render(request, 'accounts/login.html', {'companies': companies})


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
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    context = {
        'users': User.objects.all(),
        'total_users': User.objects.count(),
        'employees_count': Employee.objects.count(),
        'providers': Provider.objects.all(),
        'total_providers': Provider.objects.count(),
        'active_tickets': Ticket.objects.filter(status='active').count(),
        'pending_requests': PurchaseRequest.objects.filter(status='pending').count(),
        'employees': Employee.objects.all(),
        'ticket_lots': TicketLot.objects.all().order_by('-created_at')[:10],
        'purchases_data': [12, 19, 25, 32, 28, 35],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def employee_dashboard(request):
    """Dashboard pour l'employé"""
    from apps.tickets.models import EmployeeBalance
    from apps.purchases.models import PurchaseRequest
    from apps.menus.models import DailyMenu, Menu
    from apps.employees.models import Employee
    from datetime import datetime
    
    # Créer le profil employé s'il n'existe pas
    try:
        employee = request.user.employee_profile
        print(f"DEBUG: Employee found: {employee.user.username}")
    except Employee.DoesNotExist:
        employee = Employee.objects.create(user=request.user)
        print(f"DEBUG: Employee created: {employee.user.username}")
    
    try:
        balance = EmployeeBalance.objects.filter(employee=employee).first()
        
        # DEBUG: Vérifier les données
        print(f"DEBUG: Employee company: {employee.company}")
        print(f"DEBUG: Employee company ID: {employee.company.id if employee.company else None}")
        
        # Filtrer les menus par entreprise de l'employé
        if employee.company:
            # Afficher tous les menus disponibles des prestataires de l'entreprise
            today_menus = DailyMenu.objects.filter(
                is_available=True,
                provider__company=employee.company
            ).select_related('provider')
            
            print(f"DEBUG: Total menus found before limit: {today_menus.count()}")
            today_menus = today_menus[:3]
            print(f"DEBUG: Total menus after limit: {today_menus.count()}")
            
            # DEBUG: Afficher les détails des menus
            for menu in today_menus:
                print(f"DEBUG: Menu - ID: {menu.id}, Title: {menu.title}, Provider: {menu.provider.name}, Available: {menu.is_available}")
        else:
            # Si pas d'entreprise, afficher tous les menus disponibles
            today_menus = DailyMenu.objects.filter(
                is_available=True
            ).select_related('provider')[:3]
            print(f"DEBUG: No company, showing all menus: {today_menus.count()}")
        
        context = {
            'employee': employee,
            'balance': balance.active_tickets if balance else 0,
            'pending_purchases': PurchaseRequest.objects.filter(employee=employee, status='pending').count(),
            'today_menus': today_menus,
        }
    except Exception as e:
        print(f"DEBUG: Exception in employee_dashboard: {e}")
        context = {
            'employee': employee,
            'balance': 0,
            'pending_purchases': 0,
            'today_menus': [],
        }
    return render(request, 'dashboard/employee_dashboard.html', context)


@login_required
def validator_dashboard(request):
    """Dashboard pour le validateur"""
    context = {
        'pending_requests': PurchaseRequest.objects.filter(status='pending'),
        'total_validated': PurchaseRequest.objects.filter(status='approved').count(),
        'total_refused': PurchaseRequest.objects.filter(status='refused').count(),
    }
    return render(request, 'dashboard/validator_dashboard.html', context)


@login_required
def finance_dashboard(request):
    """Dashboard pour la direction financière"""
    context = {
        'total_tickets_sold': Ticket.objects.filter(status='used').count(),
        'total_revenue': Ticket.objects.filter(status='used').count() * 1000,
        'total_to_pay': 0,
        'monthly_data': [10, 20, 30, 40, 35, 45, 50, 55, 60, 65, 70, 75],
    }
    return render(request, 'dashboard/finance_dashboard.html', context)


@login_required
def order_meal(request):
    """Page commander un repas"""
    from apps.menus.models import DailyMenu, Menu
    from datetime import datetime
    
    try:
        employee = request.user.employee_profile
        company = employee.company
        print(f"DEBUG order_meal: Employee {employee.user.username}, Company: {company}")
    except Exception as e:
        print(f"DEBUG order_meal: Exception getting employee: {e}")
        return redirect('login')
    
    # Filtrer les menus par entreprise de l'employé
    if company:
        # Menu du jour = Uniquement les DailyMenu du jour actuel
        today_menus = DailyMenu.objects.filter(
            date=datetime.now().date(),
            is_available=True,
            provider__company=company
        ).select_related('provider')
        
        # Autres menus = Les Menu qui ne sont PAS des DailyMenu ET qui ne sont pas du jour
        # On exclut les menus qui sont aussi des DailyMenu (héritage)
        daily_menu_ids = DailyMenu.objects.filter(
            provider__company=company
        ).values_list('menu_ptr_id', flat=True)
        
        other_menus = Menu.objects.filter(
            is_available=True,
            provider__company=company
        ).exclude(
            id__in=daily_menu_ids  # Exclure les menus qui sont aussi des DailyMenu
        ).select_related('provider')
        
        print(f"DEBUG order_meal: Company {company.name}")
        print(f"DEBUG: DailyMenu IDs to exclude: {list(daily_menu_ids)}")
        print(f"DEBUG: Today menus found: {today_menus.count()}")
        print(f"DEBUG: Other menus found: {other_menus.count()}")
        
        # DEBUG: Afficher les détails
        for dm in today_menus:
            print(f"  - Today: {dm.title} (ID: {dm.id})")
        for om in other_menus:
            print(f"  - Other: {om.name} (ID: {om.id})")
    else:
        today_menus = DailyMenu.objects.filter(
            is_available=True
        ).select_related('provider')
        
        other_menus = Menu.objects.filter(
            is_available=True
        ).select_related('provider')
        
        print(f"DEBUG order_meal: No company, Today menus found: {today_menus.count()}, Other menus found: {other_menus.count()}")
    
    # DEBUG: Afficher les détails des menus
    for menu in today_menus:
        print(f"DEBUG order_meal: Today Menu - ID: {menu.id}, Title: {menu.title}, Provider: {menu.provider.name}, Available: {menu.is_available}")
    
    for menu in other_menus:
        print(f"DEBUG order_meal: Other Menu - ID: {menu.id}, Name: {menu.name}, Provider: {menu.provider.name}, Available: {menu.is_available}")
    
    # Historique des commandes
    from apps.consumption_requests.models import ConsumptionRequest
    order_history = ConsumptionRequest.objects.filter(
        employee=employee
    ).select_related('provider').order_by('-created_at')[:10]
    
    context = {
        'today_menus': today_menus,
        'other_menus': other_menus,
        'order_history': order_history,
    }
    return render(request, 'dashboard/order_meal.html', context)


@login_required
def my_tickets(request):
    """Page mes tickets"""
    try:
        employee = request.user.employee_profile
    except:
        return redirect('login')
    
    from apps.tickets.models import Ticket, TicketLot
    from apps.tickets.models import EmployeeBalance
    from apps.consumption_requests.models import ConsumptionRequest
    
    # Tickets
    active_tickets = Ticket.objects.filter(
        lot__employee=employee,
        status='active'
    ).select_related('lot')
    
    used_tickets = Ticket.objects.filter(
        lot__employee=employee,
        status='used'
    ).select_related('lot')
    
    expired_tickets = Ticket.objects.filter(
        lot__employee=employee,
        status='expired'
    ).select_related('lot')
    
    # Lots
    ticket_lots = TicketLot.objects.filter(
        employee=employee
    ).order_by('-created_at')
    
    # Consommations
    consumptions = ConsumptionRequest.objects.filter(
        employee=employee,
        status='confirmed'
    ).select_related('provider').order_by('-created_at')
    
    # Balance
    balance = EmployeeBalance.objects.filter(employee=employee).first()
    
    # Stats
    total_active = active_tickets.count()
    total_used = used_tickets.count()
    total_expired = expired_tickets.count()
    total_value = (total_active + total_used + total_expired) * 1000
    
    context = {
        'active_tickets': active_tickets,
        'used_tickets': used_tickets,
        'expired_tickets': expired_tickets,
        'ticket_lots': ticket_lots,
        'consumptions': consumptions,
        'balance': balance,
        'total_active': total_active,
        'total_used': total_used,
        'total_expired': total_expired,
        'total_value': total_value,
    }
    return render(request, 'dashboard/my_tickets.html', context)


@login_required
def provider_dashboard(request):
    """Dashboard pour le prestataire"""
    from apps.menus.models import DailyMenu
    from apps.consumption_requests.models import ConsumptionRequest
    from datetime import datetime
    
    provider = None
    try:
        provider_user = request.user.provider_profile
        provider = provider_user.provider
    except:
        pass
    
    context = {
        'provider': provider,
        'today_orders': 0,
        'pending_consumptions': ConsumptionRequest.objects.filter(provider=provider, status='pending').count() if provider else 0,
        'total_consumptions': ConsumptionRequest.objects.filter(provider=provider, status='confirmed').count() if provider else 0,
        'menus': DailyMenu.objects.filter(provider=provider, date=datetime.now().date()) if provider else [],
    }
    return render(request, 'dashboard/provider_dashboard.html', context)


def provider_menus(request):
    """Page complète des menus du prestataire"""
    from apps.menus.models import DailyMenu
    from apps.consumption_requests.models import ConsumptionRequest
    
    provider = None
    try:
        provider_user = request.user.provider_profile
        provider = provider_user.provider
    except:
        pass
    
    context = {
        'provider': provider,
    }
    return render(request, 'dashboard/provider_menus.html', context)


@login_required
def provider_transactions(request):
    """Page transactions du prestataire"""
    provider = None
    try:
        provider_user = request.user.provider_profile
        provider = provider_user.provider
    except:
        pass
    
    context = {
        'provider': provider,
    }
    return render(request, 'dashboard/provider_transactions.html', context)


@login_required
def provider_orders(request):
    """Page commandes reçues du prestataire"""
    provider = None
    try:
        provider_user = request.user.provider_profile
        provider = provider_user.provider
    except:
        pass
    
    context = {
        'provider': provider,
    }
    return render(request, 'dashboard/provider_orders.html', context)


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


@login_required
def order_menu(request):
    return render(request, 'orders/order_menu.html')


def select_company(request):
    """Sélection de l'entreprise après connexion"""
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        if company_id:
            request.session['current_company_id'] = int(company_id)
            if request.user.role == 'admin':
                return redirect('admin_dashboard')
            elif request.user.role == 'employee':
                return redirect('employee_dashboard')
            elif request.user.role == 'validator':
                return redirect('validator_dashboard')
            elif request.user.role == 'finance':
                return redirect('finance_dashboard')
    
    companies = Company.objects.filter(users=request.user)
    return render(request, 'accounts/select_company.html', {'companies': companies})


# Ajouter l'import datetime en haut du fichier
from datetime import datetime