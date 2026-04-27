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
from apps.employees.models import Employee
from apps.menus.models import DailyMenu, Menu


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
        elif user.role == 'provider':
            try:
                provider = user.provider_profile.provider
                queryset = queryset.filter(menu__provider=provider)
            except:
                queryset = queryset.none()
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
    
    @action(detail=False, methods=['post'])
    def place_cart_order(self, request):
        """Commander depuis le panier avec option anonyme"""
        if request.user.role != 'employee':
            return Response({'error': 'Réservé aux employés'}, status=status.HTTP_403_FORBIDDEN)
        
        # Vérifier l'heure limite
        now = timezone.now()
        weekday = now.weekday()
        current_time = now.time()
        
        company_id = None
        try:
            employee = request.user.employee_profile
            company_id = employee.company.id if employee.company else None
        except:
            return Response({'error': 'Profil employé introuvable'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not MenuDeadline.can_order_on_weekday(weekday, current_time, company_id):
            return Response({'error': 'Les commandes sont closes pour aujourd\'hui'}, status=status.HTTP_403_FORBIDDEN)
        
        items = request.data.get('items', [])
        is_anonymous = request.data.get('is_anonymous', False)
        
        if not items:
            return Response({'error': 'Panier vide'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = request.user.employee_profile
        except:
            return Response({'error': 'Employé introuvable'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculer le total de tickets requis
        total_tickets_required = 0
        for item in items:
            menu_id = item.get('menu_id')
            quantity = item.get('quantity', 1)
            menu_type = item.get('menu_type', 'daily')
            
            if menu_type == 'daily':
                try:
                    menu = DailyMenu.objects.get(id=menu_id, is_available=True)
                except DailyMenu.DoesNotExist:
                    return Response({'error': f'Menu du jour {menu_id} introuvable'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    menu = Menu.objects.get(id=menu_id, is_available=True)
                except Menu.DoesNotExist:
                    return Response({'error': f'Menu {menu_id} introuvable'}, status=status.HTTP_400_BAD_REQUEST)
            
            total_tickets_required += menu.price_tickets * quantity
        
        # Vérifier le solde de tickets
        from apps.tickets.models import Ticket, EmployeeBalance
        balance = EmployeeBalance.objects.filter(employee=employee).first()
        active_tickets = balance.active_tickets if balance else 0
        
        if active_tickets < total_tickets_required:
            return Response({
                'error': f'Solde insuffisant. Vous avez {active_tickets} tickets, mais {total_tickets_required} sont requis.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer les commandes
        created_orders = []
        for item in items:
            menu_id = item.get('menu_id')
            quantity = item.get('quantity', 1)
            menu_type = item.get('menu_type', 'daily')
            
            if menu_type == 'daily':
                try:
                    menu = DailyMenu.objects.get(id=menu_id, is_available=True)
                except DailyMenu.DoesNotExist:
                    return Response({'error': f'Menu du jour {menu_id} introuvable'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    menu = Menu.objects.get(id=menu_id, is_available=True)
                except Menu.DoesNotExist:
                    return Response({'error': f'Menu {menu_id} introuvable'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Créer la commande
            order = MealOrder.objects.create(
                employee=employee if not is_anonymous else None,
                menu=menu if menu_type == 'daily' else None,
                order_type=MealOrder.OrderType.ANONYMOUS if is_anonymous else MealOrder.OrderType.NORMAL,
                quantity=quantity,
                status=MealOrder.Status.PENDING
            )
            created_orders.append(order)
        
        # Déduire les tickets
        tickets_to_deduct = total_tickets_required
        tickets = Ticket.objects.filter(
            lot__employee=employee,
            status='active'
        )[:tickets_to_deduct]
        
        for ticket in tickets:
            ticket.status = 'used'
            ticket.used_at = timezone.now()
            ticket.save()
        
        # Mettre à jour le solde
        if balance:
            balance.update_balance()
        
        serializer = MealOrderListSerializer(created_orders, many=True)
        return Response({
            'message': 'Commande passée avec succès',
            'orders': serializer.data,
            'tickets_deducted': tickets_to_deduct,
            'remaining_balance': balance.active_tickets if balance else 0
        })
    
    @action(detail=False, methods=['get'])
    def can_order(self, request):
        """Vérifier si on peut commander maintenant (heure limite)"""
        now = timezone.now()
        weekday = now.weekday()
        current_time = now.time()
        
        company_id = None
        try:
            employee = request.user.employee_profile
            company_id = employee.company.id if employee.company else None
        except:
            pass
        
        can_order = MenuDeadline.can_order_on_weekday(weekday, current_time, company_id)
        
        return Response({
            'can_order': can_order,
            'current_time': current_time.strftime('%H:%M'),
            'weekday': weekday
        })