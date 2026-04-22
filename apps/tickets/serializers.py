# ticket_backend/apps/tickets/serializers.py
"""
Sérializers pour l'application tickets
"""
from rest_framework import serializers
from .models import TicketLot, Ticket, EmployeeBalance



class TicketSerializer(serializers.ModelSerializer):
    """Sérializer pour Ticket"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'lot', 'unique_code', 'status', 'status_display',
            'used_at', 'created_at', 'is_expired'
        ]
        read_only_fields = ['id', 'unique_code', 'created_at']


class TicketLotSerializer(serializers.ModelSerializer):
    """Sérializer pour TicketLot"""
    tickets = TicketSerializer(many=True, read_only=True)
    used_count = serializers.IntegerField(read_only=True)
    active_count = serializers.IntegerField(read_only=True)
    expired_count = serializers.IntegerField(read_only=True)
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = TicketLot
        fields = [
            'id', 'employee', 'employee_name', 'quantity', 'unit_value',
            'employee_part', 'company_part', 'total_amount', 'created_at',
            'expires_at', 'tickets', 'used_count', 'active_count', 'expired_count'
        ]
        read_only_fields = ['id', 'created_at', 'total_amount']


class TicketLotCreateSerializer(serializers.ModelSerializer):
    """Sérializer pour la création d'un lot de tickets"""
    
    class Meta:
        model = TicketLot
        fields = ['employee', 'quantity', 'unit_value', 'employee_part', 'company_part', 'expires_at']
    
    def create(self, validated_data):
        # Crée le lot
        lot = TicketLot.objects.create(**validated_data)
        
        # Crée les tickets individuels
        tickets = []
        for _ in range(lot.quantity):
            tickets.append(Ticket(lot=lot))
        Ticket.objects.bulk_create(tickets)
        
        # Met à jour le solde de l'employé
        if hasattr(lot.employee, 'balance'):
            lot.employee.balance.update_balance()
        
        return lot


class EmployeeBalanceSerializer(serializers.ModelSerializer):
    """Sérializer pour EmployeeBalance"""
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    employee_email = serializers.EmailField(source='employee.user.email', read_only=True)
    
    class Meta:
        model = EmployeeBalance
        fields = [
            'id', 'employee', 'employee_name', 'employee_email',
            'active_tickets', 'used_tickets_month', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']