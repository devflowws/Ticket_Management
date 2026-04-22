# apps/consumption/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import Consumption
from .serializers import ConsumptionSerializer
from apps.tickets.models import Ticket


class ConsumptionViewSet(viewsets.ModelViewSet):
    queryset = Consumption.objects.all()
    serializer_class = ConsumptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'employee':
            return self.queryset.filter(employee__user=self.request.user)
        return self.queryset
    
    def perform_create(self, serializer):
        with transaction.atomic():
            # Sauvegarder la consommation
            consumption = serializer.save()
            
            # Déduire les tickets de l'employé
            tickets = Ticket.objects.filter(
                lot__employee=consumption.employee,
                status='active'
            )[:consumption.nb_tickets]
            
            for ticket in tickets:
                ticket.status = 'used'
                ticket.used_at = consumption.date
                ticket.save()