from django.urls import path

from .views import CtaView, FaqView, FeaturesView, HeroView, LandingPageView, RolesView, StepsView

urlpatterns = [
    path('', LandingPageView.as_view(), name='presentation-landing'),
    path('hero/', HeroView.as_view(), name='presentation-hero'),
    path('features/', FeaturesView.as_view(), name='presentation-features'),
    path('steps/', StepsView.as_view(), name='presentation-steps'),
    path('roles/', RolesView.as_view(), name='presentation-roles'),
    path('faq/', FaqView.as_view(), name='presentation-faq'),
    path('cta/', CtaView.as_view(), name='presentation-cta'),
]
