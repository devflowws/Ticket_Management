# apps/purchases/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import PurchaseRequest
from .serializers import (
    PurchaseRequestListSerializer, PurchaseRequestDetailSerializer,
    PurchaseRequestCreateSerializer
)
from apps.accounts.permissions import IsAdmin, IsValidator, IsEmployee


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    """ViewSet pour les demandes d'achat"""
    queryset = PurchaseRequest.objects.select_related('employee__user', 'validated_by').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseRequestCreateSerializer
        elif self.action == 'list':
            return PurchaseRequestListSerializer
        return PurchaseRequestDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer par statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtrer par employé
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Si l'utilisateur est un employé, ne montrer que ses demandes
        if self.request.user.role == 'employee':
            queryset = queryset.filter(employee__user=self.request.user)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Créer une nouvelle demande d'achat"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        purchase_request = serializer.save()
        
        return Response(
            PurchaseRequestDetailSerializer(purchase_request).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler une demande en attente"""
        purchase_request = self.get_object()
        
        if purchase_request.status != 'pending':
            return Response(
                {'error': 'Seules les demandes en attente peuvent être annulées.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que l'utilisateur est l'employé qui a fait la demande
        if request.user.role == 'employee' and purchase_request.employee.user != request.user:
            return Response(
                {'error': 'Vous ne pouvez annuler que vos propres demandes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        purchase_request.cancel()
        return Response({'message': 'Demande annulée avec succès.'})
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Mes demandes d'achat (employé connecté)"""
        if request.user.role != 'employee':
            return Response(
                {'error': 'Cette fonction est réservée aux employés.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        requests = PurchaseRequest.objects.filter(employee__user=request.user)
        serializer = PurchaseRequestListSerializer(requests, many=True)
        return Response(serializer.data)