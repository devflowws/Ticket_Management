# apps/orders/serializers.py
from rest_framework import serializers
from .models import MealOrder


class MealOrderListSerializer(serializers.ModelSerializer):
    """Sérializer pour la liste des commandes"""
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    menu_title = serializers.CharField(source='menu.title', read_only=True)
    provider_name = serializers.CharField(source='menu.provider.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    
    class Meta:
        model = MealOrder
        fields = [
            'id', 'employee_name', 'menu_title', 'provider_name', 'quantity',
            'order_type', 'order_type_display', 'status', 'status_display',
            'created_at', 'delivered_at'
        ]


class MealOrderDetailSerializer(serializers.ModelSerializer):
    """Sérializer pour le détail d'une commande"""
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    employee_email = serializers.EmailField(source='employee.user.email', read_only=True)
    menu_title = serializers.CharField(source='menu.title', read_only=True)
    provider_name = serializers.CharField(source='menu.provider.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    delivered_by_name = serializers.CharField(source='delivered_by.get_full_name', read_only=True)
    
    class Meta:
        model = MealOrder
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'delivered_at']


class MealOrderCreateSerializer(serializers.ModelSerializer):
    """Sérializer pour la création d'une commande"""
    
    class Meta:
        model = MealOrder
        fields = [
            'menu', 'order_type', 'quantity', 'off_menu_description',
            'off_menu_price', 'for_person_name', 'for_person_phone',
            'for_person_department', 'delivery_notes'
        ]
    
    def validate(self, data):
        request = self.context.get('request')
        
        # Vérification pour commande hors menu
        if data.get('order_type') == 'off_menu':
            if not data.get('off_menu_description'):
                raise serializers.ValidationError("Description requise pour commande hors menu")
        
        # Vérification pour commande pour tiers
        if data.get('order_type') == 'for_other':
            if not data.get('for_person_name'):
                raise serializers.ValidationError("Nom requis pour commande pour tiers")
        
        # Vérification des tickets disponibles
        if request and request.user.role == 'employee':
            employee = request.user.employee_profile
            menu = data.get('menu')
            if menu:
                tickets_needed = menu.price_tickets * data.get('quantity', 1)
                if employee.balance.active_tickets < tickets_needed:
                    raise serializers.ValidationError(f"Solde insuffisant. Besoin de {tickets_needed} tickets")
        
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        employee = request.user.employee_profile if request.user.role == 'employee' else None
        
        return MealOrder.objects.create(
            employee=employee,
            **validated_data
        )