"""
URLs pour l'application accounts
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeleteProfilePhotoView, GetProfileView, RegisterView, LoginView, LogoutView, UploadProfilePhotoView, UserViewSet,
    UserDetailView, ChangePasswordView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserDetailView.as_view(), {'pk': 'me'}, name='me'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    path('upload-photo/', UploadProfilePhotoView.as_view(), name='upload_photo'),
    path('delete-photo/', DeleteProfilePhotoView.as_view(), name='delete_photo'),
    path('profile/', GetProfileView.as_view(), name='get_profile'),

]