from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CtaSerializer,
    FaqItemSerializer,
    FeatureSerializer,
    HeroSerializer,
    LandingPageSerializer,
    RoleSerializer,
    StepSerializer,
)

LANDING_PAGE_CONTENT = {
    'hero': {
        'badge': 'Plateforme de gestion des repas en entreprise',
        'title': 'Gérez vos tickets repas sans effort',
        'subtitle': (
            "TicketMeal Pro centralise l'achat, la validation et le suivi des tickets "
            'repas pour toute votre entreprise.'
        ),
        'cta_primary': 'Créer mon espace gratuitement',
        'cta_secondary': 'Découvrir les fonctionnalités',
        'stats': [
            {'label': 'Employés gérés', 'value': '500+'},
            {'label': 'Prestataires partenaires', 'value': '12'},
            {'label': 'Taux de satisfaction', 'value': '98%'},
            {'label': 'Fraude détectée', 'value': '0 FCFA'},
        ],
    },
    'features': [
        {
            'key': 'ticket-management',
            'title': 'Gestion des tickets repas',
            'description': 'Achat, attribution et suivi des tickets en temps réel.',
        },
        {
            'key': 'meal-orders',
            'title': 'Commandes de repas',
            'description': 'Consultez les menus et commandez selon les horaires définis.',
        },
        {
            'key': 'request-validation',
            'title': 'Validation des demandes',
            'description': 'Circuit de validation structuré avec preuve de paiement.',
        },
        {
            'key': 'provider-management',
            'title': 'Gestion des prestataires',
            'description': 'Suivi des restaurants partenaires et des montants dus.',
        },
        {
            'key': 'reporting',
            'title': 'Statistiques & Reporting',
            'description': 'Tableaux de bord complets et export PDF/Excel.',
        },
        {
            'key': 'mobile-app',
            'title': 'Application mobile',
            'description': 'Interface mobile pour les employés en déplacement.',
        },
    ],
    'steps': [
        {
            'order': 1,
            'title': 'Paiement Mobile Money',
            'description': 'Paiement de la part employé via Moov Money ou TMoney.',
        },
        {
            'order': 2,
            'title': 'Soumission de la preuve',
            'description': "Ajout d'un reçu ou capture d'écran de paiement.",
        },
        {
            'order': 3,
            'title': 'Validation',
            'description': 'Le responsable valide et crédite automatiquement les tickets.',
        },
        {
            'order': 4,
            'title': 'Commande & Repas',
            'description': 'Commande chez le prestataire avec les tickets disponibles.',
        },
    ],
    'roles': [
        {
            'key': 'administrator',
            'title': 'Administrateur',
            'description': 'Paramétrage global, gestion des utilisateurs et supervision.',
        },
        {
            'key': 'employee',
            'title': 'Employé',
            'description': 'Achat de tickets, commande de repas, suivi du solde.',
        },
        {
            'key': 'validator',
            'title': 'Responsable Validation',
            'description': 'Vérification des preuves et décision sur les demandes.',
        },
        {
            'key': 'provider',
            'title': 'Prestataire',
            'description': (
                'Fournit des biens/services, accepte les tickets et est payé en fin de période.'
            ),
        },
        {
            'key': 'finance',
            'title': 'Direction Financière',
            'description': 'Statistiques, contrôle des paiements et reporting.',
        },
    ],
    'faq': [
        {
            'question': 'Comment acheter des tickets repas ?',
            'answer': (
                'Soumettez une demande avec nombre de tickets et preuve de paiement.'
            ),
        },
        {
            'question': "Quelle est la part prise en charge par l'entreprise ?",
            'answer': 'La répartition employé/entreprise est définie dans les paramètres.',
        },
        {
            'question': 'Puis-je commander depuis mon téléphone ?',
            'answer': "Oui, l'API est prévue pour une application mobile dédiée.",
        },
        {
            'question': 'Que se passe-t-il si ma demande est refusée ?',
            'answer': 'Vous recevez le motif de refus et pouvez corriger puis resoumettre.',
        },
    ],
    'cta': {
        'title': 'Prêt à simplifier la gestion des repas de votre entreprise ?',
        'subtitle': 'Rejoignez les entreprises qui font confiance à TicketMeal Pro.',
        'cta_primary': 'Créer mon espace gratuitement',
        'cta_secondary': 'Voir la démo',
    },
}


@extend_schema(tags=['Presentation'])
class LandingPageView(APIView):
    @extend_schema(
        summary='Contenu complet de la landing page',
        description='Renvoie toutes les sections de la page de presentation.',
        responses=LandingPageSerializer,
    )
    def get(self, request):
        return Response(LANDING_PAGE_CONTENT)


@extend_schema(tags=['Presentation'])
class HeroView(APIView):
    @extend_schema(summary='Section hero', responses=HeroSerializer)
    def get(self, request):
        return Response(LANDING_PAGE_CONTENT['hero'])


@extend_schema(tags=['Presentation'])
class FeaturesView(APIView):
    @extend_schema(summary='Liste des fonctionnalités', responses=FeatureSerializer(many=True))
    def get(self, request):
        return Response(LANDING_PAGE_CONTENT['features'])


@extend_schema(tags=['Presentation'])
class StepsView(APIView):
    @extend_schema(summary='Parcours en 4 étapes', responses=StepSerializer(many=True))
    def get(self, request):
        return Response(LANDING_PAGE_CONTENT['steps'])


@extend_schema(tags=['Presentation'])
class RolesView(APIView):
    @extend_schema(summary='Profils utilisateurs', responses=RoleSerializer(many=True))
    def get(self, request):
        return Response(LANDING_PAGE_CONTENT['roles'])


@extend_schema(tags=['Presentation'])
class FaqView(APIView):
    @extend_schema(summary='Questions fréquentes', responses=FaqItemSerializer(many=True))
    def get(self, request):
        return Response(LANDING_PAGE_CONTENT['faq'])


@extend_schema(tags=['Presentation'])
class CtaView(APIView):
    @extend_schema(summary='Section appel a action', responses=CtaSerializer)
    def get(self, request):
        return Response(LANDING_PAGE_CONTENT['cta'])


def landing_page_view(request):
    return render(request, 'presentation/landing.html', {'landing': LANDING_PAGE_CONTENT})
