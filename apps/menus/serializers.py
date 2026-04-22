# apps/menus/serializers.py
from rest_framework import serializers
from .models import DailyMenu, MenuDeadline, MenuCategory


class DailyMenuSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    can_order_now = serializers.BooleanField(read_only=True)
    orders_count = serializers.IntegerField(source='orders_count_today', read_only=True)
    main_photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyMenu
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'orders_count_today']
    
    def get_main_photo_url(self, obj):
        if obj.main_photo:
            return obj.main_photo.url
        return None
    
    def validate(self, data):
        if data.get('order_start_time') and data.get('order_end_time'):
            if data['order_start_time'] >= data['order_end_time']:
                raise serializers.ValidationError("L'heure de début doit être avant l'heure de fin")
        return data


class MenuDeadlineSerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    
    class Meta:
        model = MenuDeadline
        fields = '__all__'


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = '__all__'