# apps/menus/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MenuViewSet, DailyMenuViewSet, MenuCategoryViewSet, EmployeeMenuViewSet
)

router = DefaultRouter()
router.register(r'menus', MenuViewSet)
router.register(r'daily-menus', DailyMenuViewSet)
router.register(r'categories', MenuCategoryViewSet)
router.register(r'employee', EmployeeMenuViewSet, basename='employee-menu')

urlpatterns = [
    path('api/menus/', include(router.urls)),
]