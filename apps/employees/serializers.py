"""
Sérializers pour l'application employees
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Employee, QuotaConfig
from apps.accounts.serializers import UserSerializer

User = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    """Sérializer pour Employee"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    remaining_quota = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_id', 'full_name', 'email',
            'department', 'position', 'phone', 'hire_date',
            'monthly_ticket_quota', 'current_month_tickets', 'remaining_quota',
            'last_quota_reset', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_month_tickets', 'last_quota_reset', 'created_at', 'updated_at']


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Sérializer détaillé pour Employee"""
    user = UserSerializer()
    ticket_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'department', 'position', 'phone', 'hire_date',
            'monthly_ticket_quota', 'current_month_tickets', 'ticket_balance',
            'last_quota_reset', 'created_at', 'updated_at'
        ]
    
    def get_ticket_balance(self, obj):
        """Récupère le solde de tickets actif de l'employé"""
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(
            lot__employee=obj,
            status='active'
        ).count()


class QuotaConfigSerializer(serializers.ModelSerializer):
    """Sérializer pour QuotaConfig"""
    
    class Meta:
        model = QuotaConfig
        fields = [
            'id', 'default_quota', 'max_quota', 'ticket_value',
            'employee_percentage', 'company_percentage', 'ticket_validity_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeQuotaUpdateSerializer(serializers.Serializer):
    """Sérializer pour la mise à jour du quota individuel"""
    monthly_ticket_quota = serializers.IntegerField(min_value=0, max_value=100)
    
    def validate_monthly_ticket_quota(self, value):
        config = QuotaConfig.get_active_config()
        if value > config.max_quota:
            raise serializers.ValidationError(
                f"Le quota ne peut pas dépasser {config.max_quota} tickets par mois."
            )
        return value