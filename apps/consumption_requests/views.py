from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ConsumptionRequest
from .serializers import ConsumptionRequestSerializer
from apps.accounts.permissions import IsEmployee, IsAdmin


class ConsumptionRequestViewSet(viewsets.ModelViewSet):
    queryset = ConsumptionRequest.objects.all()
    serializer_class = ConsumptionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'employee':
            return self.queryset.filter(employee__user=user)
        elif user.role == 'admin':
            return self.queryset
        return self.queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(employee=self.request.user.employee_profile)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        consumption_request = self.get_object()
        try:
            consumption_request.confirm(request.user)
            return Response({'message': 'Consommation confirmée', 'status': 'confirmed'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        consumption_request = self.get_object()
        reason = request.data.get('reason', '')
        consumption_request.reject(request.user, reason)
        return Response({'message': 'Consommation rejetée', 'status': 'rejected'})


class PendingConsumptionRequestsView(generics.ListAPIView):
    serializer_class = ConsumptionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return ConsumptionRequest.objects.filter(status='pending')
        return ConsumptionRequest.objects.none()