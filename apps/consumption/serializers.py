# apps/consumption/serializers.py
from rest_framework import serializers
from .models import Consumption


class ConsumptionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = Consumption
        fields = '__all__'
        read_only_fields = ['id', 'date', 'total_amount', 'company_part', 'employee_part']