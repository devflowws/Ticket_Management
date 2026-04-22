# apps/providers/serializers.py
from rest_framework import serializers
from .models import Provider, ProviderSite, ProviderCategory


class ProviderSiteSerializer(serializers.ModelSerializer):
    """Sérializer pour les sites"""
    
    class Meta:
        model = ProviderSite
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class ProviderListSerializer(serializers.ModelSerializer):
    """Sérializer pour la liste des prestataires"""
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sites_count = serializers.IntegerField(source='sites.count', read_only=True)
    
    class Meta:
        model = Provider
        fields = [
            'id', 'name', 'commercial_name', 'phone', 'email', 'city',
            'is_active', 'is_preferred', 'rating', 'balance', 'sites_count',
            'created_at'
        ]


class ProviderDetailSerializer(serializers.ModelSerializer):
    """Sérializer détaillé pour un prestataire"""
    sites = ProviderSiteSerializer(many=True, read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Provider
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_tickets_sold', 'total_amount_due', 'total_amount_paid']


class ProviderCreateUpdateSerializer(serializers.ModelSerializer):
    """Sérializer pour la création/modification"""
    sites = ProviderSiteSerializer(many=True, required=False)
    
    class Meta:
        model = Provider
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_tickets_sold', 'total_amount_due', 'total_amount_paid']
    
    def create(self, validated_data):
        sites_data = validated_data.pop('sites', [])
        provider = Provider.objects.create(**validated_data)
        
        for site_data in sites_data:
            ProviderSite.objects.create(provider=provider, **site_data)
        
        return provider
    
    def update(self, instance, validated_data):
        sites_data = validated_data.pop('sites', [])
        
        # Mettre à jour le prestataire
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les sites
        for site_data in sites_data:
            site_id = site_data.get('id')
            if site_id:
                site = ProviderSite.objects.get(id=site_id, provider=instance)
                for attr, value in site_data.items():
                    setattr(site, attr, value)
                site.save()
            else:
                ProviderSite.objects.create(provider=instance, **site_data)
        
        return instance


class ProviderCategorySerializer(serializers.ModelSerializer):
    """Sérializer pour les catégories"""
    
    class Meta:
        model = ProviderCategory
        fields = '__all__'