# apps/companies/views.py
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Company


@staff_member_required
def quota_config(request):
    """Configuration des quotas pour l'entreprise"""
    # Récupérer l'entreprise de l'utilisateur connecté
    company = request.user.company
    
    if not company:
        messages.error(request, "Aucune entreprise associée à votre compte")
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        try:
            ticket_value = int(request.POST.get('ticket_value'))
            employee_percentage = float(request.POST.get('employee_percentage'))
            default_quota = int(request.POST.get('default_quota'))
            ticket_validity_days = int(request.POST.get('ticket_validity_days'))
            
            # Mettre à jour
            company.ticket_value = ticket_value
            company.employee_percentage = employee_percentage
            company.company_percentage = 100 - employee_percentage
            company.default_quota = default_quota
            company.ticket_validity_days = ticket_validity_days
            company.save()
            
            messages.success(request, 'Configuration mise à jour avec succès')
            return redirect('quota_config')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
    
    context = {
        'company': company,
        'ticket_employee': (company.ticket_value * company.employee_percentage / 100),
        'ticket_company': (company.ticket_value * company.company_percentage / 100),
    }
    return render(request, 'companies/quota_config.html', context)