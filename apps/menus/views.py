# apps/menus/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import DailyMenu, MenuDeadline, MenuCategory
from .serializers import DailyMenuSerializer, MenuDeadlineSerializer, MenuCategorySerializer


class DailyMenuViewSet(viewsets.ModelViewSet):
    queryset = DailyMenu.objects.all()
    serializer_class = DailyMenuSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtre par date
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)
        else:
            queryset = queryset.filter(date=timezone.now().date())
        
        # Filtre par prestataire
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        # Filtrer les menus disponibles
        if self.request.query_params.get('available') == 'true':
            queryset = queryset.filter(is_available=True)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        menu = self.get_object()
        menu.is_available = not menu.is_available
        menu.save()
        return Response({'is_available': menu.is_available})


class MenuDeadlineViewSet(viewsets.ModelViewSet):
    queryset = MenuDeadline.objects.all()
    serializer_class = MenuDeadlineSerializer
    permission_classes = [permissions.IsAdminUser]


class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAdminUser]