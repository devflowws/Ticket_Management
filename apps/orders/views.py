# apps/orders/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import MealOrder
from .serializers import (
    MealOrderListSerializer, MealOrderDetailSerializer, MealOrderCreateSerializer
)
from apps.menus.models import MenuDeadline


class MealOrderViewSet(viewsets.ModelViewSet):
    queryset = MealOrder.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MealOrderListSerializer
        elif self.action == 'create':
            return MealOrderCreateSerializer
        return MealOrderDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'employee':
            queryset = queryset.filter(employee__user=user)
        elif user.role == 'admin':
            pass
        else:
            queryset = queryset.none()
        
        # Filtre par statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtre par date
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(created_at__date=date)
        
        return queryset
    
    def perform_create(self, serializer):
        # Vérifier l'heure limite
        now = timezone.now()
        weekday = now.weekday()
        current_time = now.time()
        
        if not MenuDeadline.can_order_on_weekday(weekday, current_time):
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Les commandes sont closes pour aujourd'hui")
        
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()
        if order.confirm():
            return Response({'message': 'Commande confirmée', 'status': order.status})
        return Response({'error': 'Impossible de confirmer'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        order = self.get_object()
        order.mark_as_delivered(request.user)
        return Response({'message': 'Commande livrée', 'status': order.status})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.cancel():
            return Response({'message': 'Commande annulée', 'status': order.status})
        return Response({'error': 'Impossible d\'annuler'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Commandes du jour"""
        today = timezone.now().date()
        orders = self.get_queryset().filter(created_at__date=today)
        serializer = MealOrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Mes commandes (pour employé)"""
        if request.user.role != 'employee':
            return Response({'error': 'Réservé aux employés'}, status=status.HTTP_403_FORBIDDEN)
        
        orders = MealOrder.objects.filter(employee__user=request.user)
        serializer = MealOrderListSerializer(orders, many=True)
        return Response(serializer.data)