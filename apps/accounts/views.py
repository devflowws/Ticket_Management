"""
Vues pour l'application accounts
"""
from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout, authenticate
from django.db import models as django_models
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer, ChangePasswordSerializer
)
from .permissions import IsAdmin

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des utilisateurs"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtre par rôle
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filtre par recherche
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                django_models.Q(email__icontains=search) |
                django_models.Q(first_name__icontains=search) |
                django_models.Q(last_name__icontains=search)
            )
        
        return queryset


class RegisterView(generics.CreateAPIView):
    """Inscription d'un nouvel utilisateur"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=UserCreateSerializer,
        responses={
            201: "Utilisateur créé avec succès",
            400: "Données invalides"
        },
        operation_description="Créer un nouveau compte utilisateur"
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Connexion utilisateur avec support company_id"""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email de l\'utilisateur'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Mot de passe'),
                'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de l\'entreprise (requis pour employé, validateur, finance, prestataire)')
            }
        ),
        responses={
            200: openapi.Response(
                description='Connexion réussie',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'role': openapi.Schema(type=openapi.TYPE_STRING),
                                'company': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    }
                                )
                            }
                        )
                    }
                )
            ),
            400: 'Email et mot de passe requis',
            401: 'Email ou mot de passe incorrect',
            403: 'Accès non autorisé à cette entreprise',
            404: 'Entreprise non trouvée'
        }
    )
    def post(self, request):
        from apps.companies.models import Company
        
        email = request.data.get('email')
        password = request.data.get('password')
        company_id = request.data.get('company_id')
        
        # Validation des champs requis
        if not email or not password:
            return Response(
                {'error': 'Email et mot de passe requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Authentifier l'utilisateur
        user = authenticate(request, username=email, password=password)
        
        if not user:
            return Response(
                {'error': 'Email ou mot de passe incorrect'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Vérification de l'entreprise POUR LES NON-ADMIN UNIQUEMENT
        if user.role != 'admin':
            # Les non-admin DOIVENT fournir company_id
            if not company_id:
                return Response(
                    {'error': 'Veuillez fournir votre ID entreprise'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier que l'entreprise existe
            try:
                company = Company.objects.get(id=company_id, is_active=True)
            except Company.DoesNotExist:
                return Response(
                    {'error': 'Entreprise non trouvée'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Vérifier que l'utilisateur appartient à cette entreprise
            if user.company and user.company.id != company.id:
                return Response(
                    {'error': f'Vous n\'êtes pas autorisé à accéder à l\'entreprise {company.name}'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Préparer la réponse
        response_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
            }
        }
        
        # Ajouter les informations de l'entreprise si disponible
        if user.company:
            response_data['user']['company'] = {
                'id': user.company.id,
                'name': user.company.name
            }
        elif company_id:
            try:
                company = Company.objects.get(id=company_id)
                response_data['user']['company'] = {
                    'id': company.id,
                    'name': company.name
                }
            except Company.DoesNotExist:
                pass
        
        return Response(response_data)


class LogoutView(APIView):
    """Déconnexion utilisateur"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
            }
        ),
        responses={
            200: "Déconnexion réussie",
            400: "Token invalide"
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            logout(request)
            return Response({'message': 'Déconnexion réussie.'})
        except Exception:
            return Response({'message': 'Déconnexion réussie.'})


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Détail et modification d'un utilisateur"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        # L'utilisateur peut modifier son propre profil
        if str(self.request.user.id) == self.kwargs.get('pk') or self.kwargs.get('pk') == 'me':
            return [IsAuthenticated()]
        return [IsAdmin()]
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        if pk == 'me':
            return self.request.user
        return super().get_object()


class ChangePasswordView(APIView):
    """Changement de mot de passe"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            200: "Mot de passe modifié",
            400: "Erreur de validation"
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not user.check_password(old_password):
            return Response(
                {'old_password': 'Mot de passe incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Mot de passe modifié avec succès.'})


class UploadProfilePhotoView(APIView):
    """Uploader une photo de profil"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'photo': openapi.Schema(type=openapi.TYPE_FILE, description='Fichier image (jpg, png)')
            }
        ),
        responses={
            200: "Photo uploadée avec succès",
            400: "Fichier invalide",
            413: "Fichier trop volumineux"
        }
    )
    def post(self, request):
        user = request.user
        
        # Vérifier si un fichier a été envoyé
        if 'photo' not in request.FILES:
            return Response(
                {'error': 'Aucun fichier fourni'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photo = request.FILES['photo']
        
        # Vérifier le type de fichier
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
        if photo.content_type not in allowed_types:
            return Response(
                {'error': 'Format non supporté. Utilisez JPG, PNG ou WEBP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier la taille (max 5MB)
        if photo.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'Fichier trop volumineux. Maximum 5MB'},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )
        
        # Supprimer l'ancienne photo si elle existe
        if user.profile_photo:
            old_photo_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_photo))
            if os.path.exists(old_photo_path):
                os.remove(old_photo_path)
        
        # Sauvegarder la nouvelle photo
        user.profile_photo = photo
        user.save()
        
        return Response({
            'success': True,
            'message': 'Photo de profil mise à jour avec succès',
            'photo_url': user.profile_photo.url if user.profile_photo else None
        })


class DeleteProfilePhotoView(APIView):
    """Supprimer la photo de profil"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        responses={
            200: "Photo supprimée avec succès",
            404: "Aucune photo à supprimer"
        }
    )
    def delete(self, request):
        user = request.user
        
        if not user.profile_photo:
            return Response(
                {'error': 'Aucune photo de profil à supprimer'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Supprimer le fichier
        photo_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_photo))
        if os.path.exists(photo_path):
            os.remove(photo_path)
        
        # Supprimer la référence en base
        user.profile_photo = None
        user.save()
        
        return Response({
            'success': True,
            'message': 'Photo de profil supprimée avec succès'
        })


class GetProfileView(APIView):
    """Récupérer les informations du profil avec photo"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        return Response({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'phone': user.phone,
            'profile_photo': user.profile_photo.url if user.profile_photo else None,
            'company': {
                'id': user.company.id,
                'name': user.company.name
            } if user.company else None
        })