# ticket_backend/apps/accounts/permissions.py
"""
Permissions personnalisées pour l'application accounts
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission pour les administrateurs"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsEmployee(permissions.BasePermission):
    """Permission pour les employés"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employee'
    
    def has_object_permission(self, request, view, obj):
        # Un employé peut voir/modifier son propre profil
        if hasattr(obj, 'user'):
            return request.user.id == obj.user.id
        return request.user.id == obj.id


class IsValidator(permissions.BasePermission):
    """Permission pour les responsables validation"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'validator'
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == 'validator'


class IsFinance(permissions.BasePermission):
    """Permission pour la direction financière"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'finance'
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == 'finance'


class IsAdminOrValidator(permissions.BasePermission):
    """Permission pour admin ou validateur"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.role == 'validator'
        )