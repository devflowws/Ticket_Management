"""
Vues pour l'application employees
"""
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Employee, QuotaConfig
from .serializers import (
    EmployeeSerializer, EmployeeDetailSerializer, 
    QuotaConfigSerializer, EmployeeQuotaUpdateSerializer
)
from apps.accounts.permissions import IsAdmin


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des employés"""
    queryset = Employee.objects.select_related('user').all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdmin]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EmployeeDetailSerializer
        return EmployeeSerializer
    
    def get_queryset(self):
        # Pour Swagger, retourner un queryset vide
        if getattr(self, 'swagger_fake_view', False):
            return Employee.objects.none()
            
        queryset = super().get_queryset()
        
        # Filtre par département
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department__icontains=department)
        
        # Recherche par nom ou email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        # Si l'utilisateur est un employé, ne montrer que son propre profil
        if self.request.user.is_authenticated and self.request.user.role == 'employee':
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['patch'])
    def update_quota(self, request, pk=None):
        """Met à jour le quota mensuel d'un employé"""
        employee = self.get_object()
        serializer = EmployeeQuotaUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        employee.monthly_ticket_quota = serializer.validated_data['monthly_ticket_quota']
        employee.save()
        
        return Response(EmployeeSerializer(employee).data)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Récupère le profil de l'employé connecté"""
        try:
            employee = Employee.objects.get(user=request.user)
            serializer = EmployeeDetailSerializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Profil employé non trouvé.'},
                status=status.HTTP_404_NOT_FOUND
            )


class QuotaConfigView(generics.RetrieveUpdateAPIView):
    """Vue pour la configuration des quotas"""
    queryset = QuotaConfig.objects.all()
    serializer_class = QuotaConfigSerializer
    permission_classes = [IsAdmin]
    
    def get_object(self):
        return QuotaConfig.get_active_config()