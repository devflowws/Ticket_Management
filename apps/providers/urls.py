# apps/providers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProviderViewSet, ProviderSiteViewSet, ProviderCategoryViewSet

router = DefaultRouter()
router.register(r'', ProviderViewSet, basename='provider')
router.register(r'sites', ProviderSiteViewSet, basename='provider-site')
router.register(r'categories', ProviderCategoryViewSet, basename='provider-category')

urlpatterns = [
    path('', include(router.urls)),
]