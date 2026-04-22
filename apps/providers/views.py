# apps/providers/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from .models import Provider, ProviderSite, ProviderCategory
from .serializers import (
    ProviderListSerializer, ProviderDetailSerializer, 
    ProviderCreateUpdateSerializer, ProviderSiteSerializer,
    ProviderCategorySerializer
)
from .permissions import IsProviderAdmin, CanViewProviders


class ProviderViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des prestataires"""
    queryset = Provider.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsProviderAdmin]
        else:
            self.permission_classes = [CanViewProviders]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action in ['list']:
            return ProviderListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProviderCreateUpdateSerializer
        return ProviderDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtre par recherche
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(commercial_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # Filtre par ville
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filtre par statut
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filtre par partenaire privilégié
        is_preferred = self.request.query_params.get('is_preferred')
        if is_preferred is not None:
            queryset = queryset.filter(is_preferred=is_preferred.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def sites(self, request, pk=None):
        """Récupère tous les sites d'un prestataire"""
        provider = self.get_object()
        sites = provider.sites.all()
        serializer = ProviderSiteSerializer(sites, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_site(self, request, pk=None):
        """Ajoute un site à un prestataire"""
        provider = self.get_object()
        serializer = ProviderSiteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(provider=provider)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Statistiques d'un prestataire"""
        provider = self.get_object()
        
        from apps.consumption.models import Consumption
        
        stats = Consumption.objects.filter(provider=provider).aggregate(
            total_tickets=Sum('nb_tickets'),
            total_amount=Sum('total_amount'),
            total_company_part=Sum('company_part'),
            total_employee_part=Sum('employee_part')
        )
        
        return Response({
            'provider': provider.name,
            'total_tickets_sold': provider.total_tickets_sold,
            'total_amount_due': provider.total_amount_due,
            'total_amount_paid': provider.total_amount_paid,
            'balance': provider.balance,
            'period_stats': {
                'total_tickets': stats['total_tickets'] or 0,
                'total_amount': stats['total_amount'] or 0,
                'company_part': stats['total_company_part'] or 0,
                'employee_part': stats['total_employee_part'] or 0,
            }
        })


class ProviderSiteViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des sites"""
    serializer_class = ProviderSiteSerializer
    permission_classes = [IsProviderAdmin]
    
    def get_queryset(self):
        queryset = ProviderSite.objects.all()
        
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        return queryset


class ProviderCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories"""
    queryset = ProviderCategory.objects.all()
    serializer_class = ProviderCategorySerializer
    permission_classes = [IsProviderAdmin]