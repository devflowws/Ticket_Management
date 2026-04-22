# apps/orders/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealOrderViewSet

router = DefaultRouter()
router.register(r'', MealOrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]