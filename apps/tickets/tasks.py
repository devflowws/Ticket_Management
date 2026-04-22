# ticket_backend/apps/tickets/tasks.py
"""
Tâches asynchrones pour l'application tickets
"""
from celery import shared_task
from django.utils import timezone
from .models import TicketLot, Ticket


@shared_task
def expire_tickets():
    """
    Tâche Celery pour expirer automatiquement les tickets
    À exécuter quotidiennement
    """
    now = timezone.now()
    
    expired_lots = TicketLot.objects.filter(
        expires_at__lt=now,
        tickets__status='active'
    ).distinct()
    
    total_expired = 0
    for lot in expired_lots:
        expired_count = Ticket.objects.filter(
            lot=lot,
            status='active'
        ).update(status='expired')
        total_expired += expired_count
        
        if hasattr(lot.employee, 'balance'):
            lot.employee.balance.update_balance()
    
    return f"{total_expired} tickets expirés"