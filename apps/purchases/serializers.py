# apps/purchases/serializers.py
from rest_framework import serializers
from .models import PurchaseRequest
from apps.employees.serializers import EmployeeSerializer


class PurchaseRequestListSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PurchaseRequest
        fields = ['id', 'employee_name', 'quantity', 'total_employee_amount', 'status', 'status_display', 'created_at']


class PurchaseRequestDetailSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    validated_by_name = serializers.CharField(source='validated_by.get_full_name', read_only=True)
    
    class Meta:
        model = PurchaseRequest
        fields = '__all__'


class PurchaseRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = ['quantity', 'payment_method', 'payment_reference', 'payment_proof']
    
    def validate_quantity(self, value):
        request = self.context.get('request')
        employee = request.user.employee_profile
        
        # Vérification du quota
        remaining = employee.monthly_ticket_quota - employee.current_month_tickets
        if value > remaining:
            raise serializers.ValidationError(
                f"Vous ne pouvez demander que {remaining} tickets maximum ce mois."
            )
        
        if value <= 0:
            raise serializers.ValidationError("La quantite doit etre superieure a 0.")
        
        if value > 50:
            raise serializers.ValidationError("Vous ne pouvez pas demander plus de 50 tickets par demande.")
        
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        employee = request.user.employee_profile
        
        return PurchaseRequest.objects.create(
            employee=employee,
            **validated_data
        )