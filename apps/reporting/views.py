# apps/reporting/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.purchases.models import PurchaseRequest
from apps.consumption_requests.models import ConsumptionRequest
from apps.employees.models import Employee
from apps.providers.models import Provider
from apps.tickets.models import Ticket, TicketLot
from .exports import export_to_excel, export_to_pdf
from .serializers import MonthlyReportSerializer, ProviderReportSerializer, EmployeeReportSerializer


class MonthlyReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        
        # Achats du mois
        purchases = PurchaseRequest.objects.filter(
            created_at__year=year,
            created_at__month=month,
            status='approved'
        ).aggregate(
            total_tickets=Sum('quantity'),
            total_amount=Sum('total_employee_amount'),
            total_company=Sum('total_company_amount')
        )
        
        # Consommations du mois
        consumptions = ConsumptionRequest.objects.filter(
            created_at__year=year,
            created_at__month=month,
            status='confirmed'
        ).aggregate(
            total_tickets=Sum('nb_tickets')
        )
        
        # Employés actifs
        active_employees = Employee.objects.filter(
            user__is_active=True
        ).count()
        
        # Prestataires actifs
        active_providers = Provider.objects.filter(is_active=True).count()
        
        # Tickets expirés
        expired_tickets = Ticket.objects.filter(
            status='expired',
            lot__expires_at__year=year,
            lot__expires_at__month=month
        ).count()
        
        result = {
            'year': year,
            'month': month,
            'period': f"{year}-{month:02d}",
            'purchases': {
                'total_tickets': purchases['total_tickets'] or 0,
                'total_employee_amount': float(purchases['total_amount'] or 0),
                'total_company_amount': float(purchases['total_company'] or 0),
            },
            'consumptions': {
                'total_tickets': consumptions['total_tickets'] or 0,
            },
            'summary': {
                'active_employees': active_employees,
                'active_providers': active_providers,
                'expired_tickets': expired_tickets,
            }
        }
        
        return Response(result)


class ProviderSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)
        
        providers = Provider.objects.filter(is_active=True)
        result = []
        
        for provider in providers:
            # Tickets utilisés chez ce prestataire
            consumptions = ConsumptionRequest.objects.filter(
                provider=provider,
                status='confirmed',
                created_at__year=year,
                created_at__month=month
            ).aggregate(
                total_tickets=Sum('nb_tickets')
            )
            
            total_tickets = consumptions['total_tickets'] or 0
            # Valeur unitaire du ticket (à configurer)
            ticket_value = 1000
            
            result.append({
                'provider_id': provider.id,
                'provider_name': provider.name,
                'city': provider.city,
                'total_tickets_used': total_tickets,
                'total_amount': total_tickets * ticket_value,
                'company_part': total_tickets * ticket_value * 0.6,
                'employee_part': total_tickets * ticket_value * 0.4,
            })
        
        return Response(result)


class EmployeeSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        employees = Employee.objects.select_related('user').all()
        result = []
        
        for employee in employees:
            # Tickets achetés
            purchased = PurchaseRequest.objects.filter(
                employee=employee,
                status='approved'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            # Tickets utilisés
            used = ConsumptionRequest.objects.filter(
                employee=employee,
                status='confirmed'
            ).aggregate(total=Sum('nb_tickets'))['total'] or 0
            
            # Solde actuel
            balance = Ticket.objects.filter(
                lot__employee=employee,
                status='active'
            ).count()
            
            result.append({
                'employee_id': employee.id,
                'employee_name': employee.user.get_full_name(),
                'email': employee.user.email,
                'department': employee.department,
                'tickets_purchased': purchased,
                'tickets_used': used,
                'remaining_tickets': balance,
            })
        
        return Response(result)


class ExportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        export_type = request.query_params.get('type', 'excel')
        report_type = request.query_params.get('report', 'monthly')
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)
        
        if report_type == 'providers':
            view = ProviderSummaryView()
            data = view.get(request).data
            filename = f"rapport_prestataires_{year}_{month}"
            title = f"Rapport prestataires - {year}-{month}"
        elif report_type == 'employees':
            view = EmployeeSummaryView()
            data = view.get(request).data
            filename = f"rapport_employes_{year}_{month}"
            title = f"Rapport employés - {year}-{month}"
        else:
            view = MonthlyReportView()
            data = [view.get(request).data]
            filename = f"rapport_mensuel_{year}_{month}"
            title = f"Rapport mensuel - {year}-{month}"
        
        if export_type == 'pdf':
            return export_to_pdf(data, filename, title)
        else:
            return export_to_excel(data, filename, report_type)