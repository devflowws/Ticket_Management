# apps/validations/views.py
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import ValidationLog
from apps.purchases.models import PurchaseRequest
from apps.purchases.serializers import PurchaseRequestListSerializer, PurchaseRequestDetailSerializer
from apps.accounts.permissions import IsValidator, IsAdmin


class PendingRequestsView(generics.ListAPIView):
    """Vue pour les demandes en attente de validation"""
    serializer_class = PurchaseRequestListSerializer
    permission_classes = [IsValidator | IsAdmin]
    
    def get_queryset(self):
        return PurchaseRequest.objects.filter(status='pending').order_by('created_at')


class ValidateRequestView(generics.GenericAPIView):
    """Vue pour valider une demande"""
    permission_classes = [IsValidator | IsAdmin]
    
    def post(self, request, pk=None):
        try:
            purchase_request = PurchaseRequest.objects.get(pk=pk, status='pending')
        except PurchaseRequest.DoesNotExist:
            return Response(
                {'error': 'Demande non trouvée ou déjà traitée.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        comment = request.data.get('comment', '')
        
        # Approuver la demande et créer les tickets
        lot = purchase_request.approve(request.user, comment)
        
        # Enregistrer dans le journal
        ValidationLog.objects.create(
            purchase_request=purchase_request,
            validator=request.user,
            decision='approved',
            comment=comment
        )
        
        return Response({
            'message': 'Demande approuvée avec succès.',
            'ticket_lot_id': lot.id,
            'quantity': lot.quantity
        })


class RefuseRequestView(generics.GenericAPIView):
    """Vue pour refuser une demande"""
    permission_classes = [IsValidator | IsAdmin]
    
    def post(self, request, pk=None):
        try:
            purchase_request = PurchaseRequest.objects.get(pk=pk, status='pending')
        except PurchaseRequest.DoesNotExist:
            return Response(
                {'error': 'Demande non trouvée ou déjà traitée.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        reason = request.data.get('reason', '')
        if not reason:
            return Response(
                {'error': 'Un motif de refus est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_request.refuse(request.user, reason)
        
        # Enregistrer dans le journal
        ValidationLog.objects.create(
            purchase_request=purchase_request,
            validator=request.user,
            decision='refused',
            comment=reason
        )
        
        return Response({'message': 'Demande refusée.'})


class ValidationHistoryView(generics.ListAPIView):
    """Vue pour l'historique des validations"""
    serializer_class = PurchaseRequestListSerializer
    permission_classes = [IsValidator | IsAdmin]
    
    def get_queryset(self):
        return PurchaseRequest.objects.filter(
            Q(status='approved') | Q(status='refused')
        ).order_by('-validated_at')