"""
Vues pour l'application tickets
"""
from rest_framework import viewsets, generics, status, serializers  # Ajouter serializers ici
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import TicketLot, Ticket, EmployeeBalance
from .serializers import (
    TicketLotSerializer, TicketLotCreateSerializer, 
    TicketSerializer, EmployeeBalanceSerializer
)
from apps.accounts.permissions import IsAdmin, IsEmployee


class TicketLotViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des lots de tickets"""
    queryset = TicketLot.objects.select_related('employee__user').all()
    serializer_class = TicketLotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdmin]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TicketLotCreateSerializer
        return TicketLotSerializer
    
    def get_queryset(self):
        # Pour Swagger, retourner un queryset vide
        if getattr(self, 'swagger_fake_view', False):
            return TicketLot.objects.none()
            
        queryset = super().get_queryset()
        
        # Filtre par employé
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Si l'utilisateur est un employé, ne montrer que ses lots
        if self.request.user.is_authenticated and self.request.user.role == 'employee':
            try:
                employee = self.request.user.employee_profile
                queryset = queryset.filter(employee=employee)
            except:
                queryset = queryset.none()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def expire_lot(self, request, pk=None):
        """Expire tous les tickets actifs d'un lot"""
        lot = self.get_object()
        
        expired_count = Ticket.objects.filter(
            lot=lot,
            status='active'
        ).update(status='expired')
        
        # Met à jour le solde
        if hasattr(lot.employee, 'balance'):
            lot.employee.balance.update_balance()
        
        return Response({
            'message': f'{expired_count} tickets ont été expirés.',
            'expired_count': expired_count
        })


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour la consultation des tickets"""
    queryset = Ticket.objects.select_related('lot__employee__user').all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Pour Swagger, retourner un queryset vide
        if getattr(self, 'swagger_fake_view', False):
            return Ticket.objects.none()
            
        queryset = super().get_queryset()
        
        # Filtre par statut
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtre par lot
        lot_id = self.request.query_params.get('lot')
        if lot_id:
            queryset = queryset.filter(lot_id=lot_id)
        
        # Si l'utilisateur est un employé, ne montrer que ses tickets
        if self.request.user.is_authenticated and self.request.user.role == 'employee':
            try:
                employee = self.request.user.employee_profile
                queryset = queryset.filter(lot__employee=employee)
            except:
                queryset = queryset.none()
        
        return queryset


class EmployeeBalanceView(generics.RetrieveAPIView):
    """Vue pour le solde de tickets d'un employé"""
    serializer_class = EmployeeBalanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        employee_id = self.kwargs.get('employee_id')
        
        # Si l'utilisateur est un employé, vérifier qu'il consulte son propre solde
        if self.request.user.is_authenticated and self.request.user.role == 'employee':
            try:
                employee = self.request.user.employee_profile
                if employee.id != employee_id:
                    raise PermissionError
            except:
                raise PermissionError
        
        balance, created = EmployeeBalance.objects.get_or_create(employee_id=employee_id)
        balance.update_balance()  # Rafraîchit le solde
        return balance


class ExpireTicketsView(generics.GenericAPIView):
    """Vue pour expirer automatiquement les tickets"""
    permission_classes = [IsAdmin]
    
    # Ajouter un serializer factice pour Swagger
    serializer_class = serializers.Serializer
    
    def post(self, request):
        """Expire les tickets dont la date d'expiration est dépassée"""
        now = timezone.now()
        
        # Trouve les lots expirés avec des tickets actifs
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
            
            # Met à jour le solde
            if hasattr(lot.employee, 'balance'):
                lot.employee.balance.update_balance()
        
        return Response({
            'message': f'{total_expired} tickets expirés ont été traités.',
            'expired_count': total_expired
        })