# apps/providers/permissions.py
from rest_framework import permissions


class IsProviderAdmin(permissions.BasePermission):
    """Permission pour l'administration des prestataires"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'finance']
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role in ['admin', 'finance']


class CanViewProviders(permissions.BasePermission):
    """Permission pour voir les prestataires"""
    
    def has_permission(self, request, view):
        # Tout le monde authentifié peut voir les prestataires
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated