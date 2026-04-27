# apps/menus/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Menu, DailyMenu, MenuCategory
from .serializers import MenuSerializer, DailyMenuSerializer, MenuCategorySerializer


class IsProviderOrAdmin(permissions.BasePermission):
    """Permission pour les prestataires et admins"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Admin a tous les droits
        if request.user.role == 'admin':
            return True
        # Prestataire peut gérer ses menus
        if request.user.role == 'provider':
            # Pour les actions de création, modification, suppression
            if view.action in ['create', 'update', 'partial_update', 'destroy', 'toggle_availability']:
                return True
            # Pour la lecture, on filtre dans get_queryset
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'provider':
            # Vérifier que le prestataire possède ce menu
            try:
                provider = request.user.provider_profile.provider
                return obj.provider == provider
            except:
                return False
        return False


class DailyMenuViewSet(viewsets.ModelViewSet):
    """ViewSet pour les menus du jour"""
    serializer_class = DailyMenuSerializer
    permission_classes = [IsProviderOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = DailyMenu.objects.all()
        
        # Filtrer par rôle
        if user.role == 'provider':
            try:
                provider = user.provider_profile.provider
                queryset = queryset.filter(provider=provider)
            except:
                return DailyMenu.objects.none()
        elif user.role == 'employee':
            # Les employés voient tous les menus disponibles
            queryset = queryset.filter(is_available=True, date=timezone.now().date())
        
        # Filtre par date (optionnel)
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)
        
        # Filtre par prestataire
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        # Filtrer les menus disponibles
        if self.request.query_params.get('available') == 'true':
            queryset = queryset.filter(is_available=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Lors de la création d'un menu, l'associer au prestataire connecté"""
        user = self.request.user
        
        if user.role == 'provider':
            try:
                provider = user.provider_profile.provider
                serializer.save(provider=provider, created_by=user)
            except:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Vous n'êtes pas associé à un prestataire")
        else:
            serializer.save(created_by=user)
    
    def perform_update(self, serializer):
        """Mise à jour d'un menu"""
        user = self.request.user
        if user.role == 'provider':
            try:
                provider = user.provider_profile.provider
                serializer.save(provider=provider, created_by=user)
            except:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Vous n'êtes pas associé à un prestataire")
        else:
            serializer.save(created_by=user)
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """Activer/Désactiver un menu"""
        menu = self.get_object()
        menu.is_available = not menu.is_available
        menu.save()
        return Response({
            'is_available': menu.is_available,
            'message': f"Menu {'activé' if menu.is_available else 'désactivé'} avec succès"
        })


class MenuDeadlineViewSet(viewsets.ModelViewSet):
    queryset = MenuDeadline.objects.all()
    serializer_class = MenuDeadlineSerializer
    permission_classes = [permissions.IsAdminUser]


class MenuCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories de menus"""
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company']


class EmployeeMenuViewSet(viewsets.ViewSet):
    """ViewSet pour les menus accessibles aux employés avec filtres"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Lister les menus avec filtres pour les employés"""
        from datetime import datetime
        from apps.employees.models import Employee
        
        try:
            employee = request.user.employee_profile
            company = employee.company
        except:
            return Response({'error': 'Profil employé introuvable'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Paramètres de filtrage
        menu_filter = request.query_params.get('menu_filter', 'all')  # today, other, all
        meal_type = request.query_params.get('meal_type', 'all')     # main, starter, drink, side, dessert, all
        
        # Menu du jour = Uniquement les DailyMenu du jour actuel
        if company:
            today_menus = DailyMenu.objects.filter(
                date=datetime.now().date(),
                is_available=True,
                provider__company=company
            ).select_related('provider')
            
            # Autres menus = Les Menu qui ne sont PAS des DailyMenu
            daily_menu_ids = DailyMenu.objects.filter(
                provider__company=company
            ).values_list('menu_ptr_id', flat=True)
            
            other_menus = Menu.objects.filter(
                is_available=True,
                provider__company=company
            ).exclude(
                id__in=daily_menu_ids
            ).select_related('provider')
        else:
            today_menus = DailyMenu.objects.filter(
                date=datetime.now().date(),
                is_available=True
            ).select_related('provider')
            
            # S'il n'y a pas d'entreprise, on exclut les DailyMenu des Menu
            daily_menu_ids = DailyMenu.objects.all().values_list('menu_ptr_id', flat=True)
            other_menus = Menu.objects.filter(
                is_available=True
            ).exclude(
                id__in=daily_menu_ids
            ).select_related('provider')
                    'active': active_menus,
                    'daily_today': daily_menus_today
                },
                'orders': {
                    'today': today_orders,
                    'pending_consumptions': pending_consumptions,
                    'total_consumptions': total_consumptions
                },
                'revenue': {
                    'today': today_revenue,
                    'week': week_revenue
                },
                'customers': {
                    'unique_week': unique_customers
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProviderStatsViewSet(viewsets.ViewSet):
    """ViewSet pour les stats du prestataire"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Récupérer les stats du prestataire"""
        user = request.user
        if user.role != 'provider':
            return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            provider = user.provider_profile.provider
            today = timezone.now().date()
            week_ago = today - timezone.timedelta(days=7)
            
            # Stats des menus
            total_menus = DailyMenu.objects.filter(provider=provider).count()
            active_menus = DailyMenu.objects.filter(provider=provider, is_available=True).count()
            daily_menus_today = DailyMenu.objects.filter(provider=provider, is_daily=True, date=today).count()
            
            # Importer les modèles de commandes et consommations
            try:
                from apps.consumption_requests.models import ConsumptionRequest
                from apps.orders.models import Order
                
                # Stats des commandes
                today_orders = Order.objects.filter(menu__provider=provider, created_at__date=today).count()
                pending_consumptions = ConsumptionRequest.objects.filter(provider=provider, status='pending').count()
                total_consumptions = ConsumptionRequest.objects.filter(provider=provider, status='confirmed').count()
                
                # Revenus (basés sur le prix des tickets)
                from apps.tickets.models import Ticket
                ticket_value = 500  # Valeur d'un ticket en FCFA
                
                today_revenue = Order.objects.filter(menu__provider=provider, created_at__date=today).count() * ticket_value
                week_revenue = Order.objects.filter(menu__provider=provider, created_at__date__gte=week_ago).count() * ticket_value
                
                # Clients uniques cette semaine
                unique_customers = Order.objects.filter(
                    menu__provider=provider,
                    created_at__date__gte=week_ago
                ).values('employee').distinct().count()
                
            except:
                today_orders = 0
                pending_consumptions = 0
                total_consumptions = 0
                today_revenue = 0
                week_revenue = 0
                unique_customers = 0
            
            return Response({
                'menus': {
                    'total': total_menus,
                    'active': active_menus,
                    'daily_today': daily_menus_today
                },
                'orders': {
                    'today': today_orders,
                    'pending_consumptions': pending_consumptions,
                    'total_consumptions': total_consumptions
                },
                'revenue': {
                    'today': today_revenue,
                    'week': week_revenue
                },
                'customers': {
                    'unique_week': unique_customers
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)