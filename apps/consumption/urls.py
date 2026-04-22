# apps/consumption/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsumptionViewSet

router = DefaultRouter()
router.register(r'', ConsumptionViewSet, basename='consumption')

urlpatterns = [
    path('', include(router.urls)),
]