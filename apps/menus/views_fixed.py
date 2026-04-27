# apps/menus/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
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
        # Prestataire peut voir et modifier ses propres menus
        if request.user.role == 'provider':
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout modifier
        if request.user.role == 'admin':
            return True
        # Prestataire peut modifier uniquement ses menus
        if request.user.role == 'provider' and hasattr(obj, 'provider'):
            return obj.provider == request.user.provider_profile.provider
        return False


class MenuViewSet(viewsets.ModelViewSet):
    """ViewSet pour les menus permanents"""
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsProviderOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['provider', 'meal_type', 'is_available']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'provider':
            provider = user.provider_profile.provider
            return Menu.objects.filter(provider=provider)
        elif user.role == 'admin':
            return Menu.objects.all()
        return Menu.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'provider':
            provider = user.provider_profile.provider
            serializer.save(provider=provider, created_by=user)
        elif user.role == 'admin':
            serializer.save(created_by=user)


class DailyMenuViewSet(viewsets.ModelViewSet):
    """ViewSet pour les menus du jour"""
    queryset = DailyMenu.objects.all()
    serializer_class = DailyMenuSerializer
    permission_classes = [IsProviderOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['provider', 'date', 'meal_type', 'is_available']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'provider':
            provider = user.provider_profile.provider
            return DailyMenu.objects.filter(provider=provider)
        elif user.role == 'admin':
            return DailyMenu.objects.all()
        return DailyMenu.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'provider':
            provider = user.provider_profile.provider
            serializer.save(provider=provider, created_by=user)
        elif user.role == 'admin':
            serializer.save(created_by=user)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Lister les menus du jour"""
        today = timezone.now().date()
        user = request.user
        
        if user.role == 'provider':
            provider = user.provider_profile.provider
            menus = DailyMenu.objects.filter(provider=provider, date=today)
        elif user.role == 'admin':
            menus = DailyMenu.objects.filter(date=today)
        else:
            return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(menus, many=True)
        return Response(serializer.data)


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
        
        # Filtrer par type de plat si nécessaire
        if meal_type != 'all':
            today_menus = today_menus.filter(meal_type=meal_type)
            other_menus = other_menus.filter(meal_type=meal_type)
        
        # Appliquer le filtre principal
        if menu_filter == 'today':
            menus = today_menus
            serializer = DailyMenuSerializer(menus, many=True)
            return Response({
                'menus': serializer.data,
                'menu_filter': 'today',
                'meal_type': meal_type,
                'count': len(serializer.data)
            })
        elif menu_filter == 'other':
            menus = other_menus
            serializer = MenuSerializer(menus, many=True)
            return Response({
                'menus': serializer.data,
                'menu_filter': 'other',
                'meal_type': meal_type,
                'count': len(serializer.data)
            })
        else:  # all
            today_data = DailyMenuSerializer(today_menus, many=True).data
            other_data = MenuSerializer(other_menus, many=True).data
            
            # Ajouter un champ pour distinguer les types
            for item in today_data:
                item['menu_category'] = 'daily'
            for item in other_data:
                item['menu_category'] = 'permanent'
            
            return Response({
                'today_menus': today_data,
                'other_menus': other_data,
                'total_count': len(today_data) + len(other_data),
                'menu_filter': 'all',
                'meal_type': meal_type
            })
    
    @action(detail=False, methods=['get'])
    def meal_types(self, request):
        """Lister les types de plats disponibles"""
        meal_types = [
            {'value': 'all', 'label': 'Tous types'},
            {'value': 'main', 'label': 'Plats principaux'},
            {'value': 'starter', 'label': 'Entrées'},
            {'value': 'drink', 'label': 'Boissons'},
            {'value': 'side', 'label': 'Accompagnements'},
            {'value': 'dessert', 'label': 'Desserts'}
        ]
        return Response(meal_types)
    
    @action(detail=False, methods=['get'])
    def filters_info(self, request):
        """Informations sur les filtres disponibles"""
        return Response({
            'menu_filters': [
                {'value': 'all', 'label': 'Tous'},
                {'value': 'today', 'label': 'Menu du jour'},
                {'value': 'other', 'label': 'Autres menus'}
            ],
            'meal_types': [
                {'value': 'all', 'label': 'Tous types'},
                {'value': 'main', 'label': 'Plats principaux'},
                {'value': 'starter', 'label': 'Entrées'},
                {'value': 'drink', 'label': 'Boissons'},
                {'value': 'side', 'label': 'Accompagnements'},
                {'value': 'dessert', 'label': 'Desserts'}
            ]
        })


class MenuCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories de menus"""
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company']
