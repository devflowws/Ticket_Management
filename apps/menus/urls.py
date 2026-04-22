# apps/menus/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyMenuViewSet, MenuDeadlineViewSet, MenuCategoryViewSet

router = DefaultRouter()
router.register(r'daily', DailyMenuViewSet, basename='menu-daily')
router.register(r'deadlines', MenuDeadlineViewSet, basename='menu-deadline')
router.register(r'categories', MenuCategoryViewSet, basename='menu-category')

urlpatterns = [
    path('', include(router.urls)),
]