# apps/core/api_views.py
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

User = get_user_model()
from apps.employees.models import Employee
from apps.providers.models import Provider
from apps.tickets.models import TicketLot, Ticket


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_add_user(request):
    """Ajouter un utilisateur"""
    try:
        data = json.loads(request.body)
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role']
        )
        
        # Si c'est un employé, créer son profil
        if data['role'] == 'employee':
            Employee.objects.create(
                user=user,
                department=data.get('department', '')
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Utilisateur {user.get_full_name()} créé avec succès',
            'user': {
                'id': user.id,
                'full_name': user.get_full_name(),
                'email': user.email,
                'role': user.role,
                'department': data.get('department', '')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_edit_user(request, user_id):
    """Modifier un utilisateur"""
    try:
        data = json.loads(request.body)
        user = User.objects.get(id=user_id)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.role = data.get('role', user.role)
        
        if data.get('password'):
            user.set_password(data['password'])
        
        user.save()
        
        # Mettre à jour le département si c'est un employé
        if hasattr(user, 'employee_profile'):
            user.employee_profile.department = data.get('department', '')
            user.employee_profile.save()
        
        return JsonResponse({'success': True, 'message': 'Utilisateur modifié avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_delete_user(request, user_id):
    """Supprimer un utilisateur"""
    try:
        user = User.objects.get(id=user_id)
        # Ne pas supprimer l'admin principal
        if user.role == 'admin' and User.objects.filter(role='admin').count() == 1:
            return JsonResponse({'success': False, 'error': 'Impossible de supprimer le seul administrateur'})
        
        user.delete()
        return JsonResponse({'success': True, 'message': 'Utilisateur supprimé avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_add_provider(request):
    """Ajouter un prestataire"""
    try:
        data = json.loads(request.body)
        provider = Provider.objects.create(
            name=data['name'],
            email=data.get('email', ''),
            phone=data['phone'],
            address=data.get('address', ''),
            city=data.get('city', ''),
            is_active=True
        )
        return JsonResponse({
            'success': True,
            'message': f'Prestataire {provider.name} ajouté avec succès',
            'provider': {
                'id': provider.id,
                'name': provider.name,
                'phone': provider.phone,
                'city': provider.city
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_edit_provider(request, provider_id):
    """Modifier un prestataire"""
    try:
        data = json.loads(request.body)
        provider = Provider.objects.get(id=provider_id)
        provider.name = data.get('name', provider.name)
        provider.email = data.get('email', provider.email)
        provider.phone = data.get('phone', provider.phone)
        provider.address = data.get('address', provider.address)
        provider.city = data.get('city', provider.city)
        provider.save()
        return JsonResponse({'success': True, 'message': 'Prestataire modifié avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_delete_provider(request, provider_id):
    """Supprimer un prestataire"""
    try:
        provider = Provider.objects.get(id=provider_id)
        provider.delete()
        return JsonResponse({'success': True, 'message': 'Prestataire supprimé avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_generate_ticket_lot(request):
    """Générer un lot de tickets"""
    try:
        from datetime import datetime, timedelta
        data = json.loads(request.body)
        employee = Employee.objects.get(id=data['employee_id'])
        quantity = int(data['quantity'])
        
        from apps.employees.models import QuotaConfig
        config = QuotaConfig.get_active_config()
        
        lot = TicketLot.objects.create(
            employee=employee,
            quantity=quantity,
            unit_value=config.ticket_value,
            employee_part=config.ticket_value * config.employee_percentage / 100,
            company_part=config.ticket_value * config.company_percentage / 100,
            expires_at=datetime.now() + timedelta(days=config.ticket_validity_days)
        )
        
        # Créer les tickets individuels
        tickets = [Ticket(lot=lot) for _ in range(quantity)]
        Ticket.objects.bulk_create(tickets)
        
        return JsonResponse({
            'success': True,
            'message': f'Lot de {quantity} tickets généré pour {employee.user.get_full_name()}',
            'lot_id': lot.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})