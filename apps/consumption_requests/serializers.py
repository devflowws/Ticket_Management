from rest_framework import serializers
from .models import ConsumptionRequest


class ConsumptionRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ConsumptionRequest
        fields = '__all__'
        read_only_fields = ['id', 'status', 'created_at', 'confirmed_at', 'confirmed_by']