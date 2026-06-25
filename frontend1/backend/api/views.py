import json
import random
import uuid
import urllib.error
import urllib.request
import logging
from decimal import Decimal
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Count, Sum
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdminRole
from .models import User, Wallet, Transaction, QRCodeRecord, FraudReport, CommissionRecord, Location, PartnerServiceRequest
from .serializers import (
    UserSerializer,
    PartnerSerializer,
    RegisterSerializer,
    LoginSerializer,
    WalletSerializer,
    TransactionSerializer,
    TransactionCreateSerializer,
    PartnerServiceRequestSerializer,
    PartnerServiceRequestCreateSerializer,
    QRScanSerializer,
    QRScanResultSerializer,
    DashboardSerializer,
    FraudReportSerializer,
    CommissionSerializer,
    LocationSerializer,
    LocationDetailSerializer,
)

logger = logging.getLogger(__name__)


class CustomerListAPIView(generics.ListAPIView):
    """
    Liste tous les clients (pour les commerçants/partenaires/administrateurs
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtrer les utilisateurs avec le rôle customer
        qs = User.objects.filter(role='customer', statut='actif')
        # Recherche par nom/email/téléphone si un paramètre search est passé
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(
                prenom__icontains=search
            ) | qs.filter(
                nom__icontains=search
            ) | qs.filter(
                telephone__icontains=search
            )
        return qs


class APIRootView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'message': 'SmartChange API root',
            'available_endpoints': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'me': '/api/auth/me/',
                'refresh': '/api/auth/refresh/',
                'wallet': '/api/wallet/',
                'wallet_withdraw': '/api/wallet/withdraw/',
                'wallet_recharge': '/api/wallet/recharge/',
                'transactions': '/api/transactions/',
                'partners': '/api/partners/',
                'dashboard': '/api/dashboard/',
                'admin_users': '/api/admin/users/',
                'admin_transactions': '/api/admin/transactions/',
                'admin_fraud': '/api/admin/fraud/',
                'admin_commissions': '/api/admin/commissions/',
            }
        })


class APIDocsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'title': 'SmartChange API documentation',
            'description': 'Use the listed endpoints to interact with SmartChange.',
            'authentication': 'Bearer token required for protected routes.',
            'endpoints': {
                '/api/auth/register/': 'POST user registration',
                '/api/auth/login/': 'POST login and get tokens',
                '/api/auth/me/': 'GET current authenticated user',
                '/api/auth/refresh/': 'POST refresh token',
                '/api/wallet/': 'GET authenticated user wallet',
                '/api/wallet/withdraw/': 'POST withdraw wallet balance',
                '/api/wallet/recharge/': 'POST/GET recharge wallet via FedaPay',
                '/api/payments/initiate/': 'POST start a FedaPay payment',
                '/api/transactions/': 'GET list or POST create a transaction',
                '/api/partners/': 'GET active partners list',
                '/api/qr/scan/': 'POST scan a QR reference',
                '/api/dashboard/': 'GET dashboard metrics',
                '/api/admin/users/': 'GET all users (admin only)',
                '/api/admin/transactions/': 'GET all transactions (admin only)',
                '/api/admin/fraud/': 'GET fraud reports (admin only)',
                '/api/admin/commissions/': 'GET commission records (admin only)',
            }
        })


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        logger.info(f"Login attempt - Data: {request.data}")
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Login validation failed - Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        logger.info(f"Login successful for user {user.id}")
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PartnerListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PartnerSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role='partner', statut='actif')
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(nom_boutique__icontains=query) | queryset.filter(adresse__icontains=query)
        return queryset


class PartnerServiceRequestView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PartnerServiceRequestCreateSerializer
        return PartnerServiceRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'merchant':
            return PartnerServiceRequest.objects.filter(merchant=user).order_by('-created_at')
        if user.role == 'partner':
            return PartnerServiceRequest.objects.filter(partner=user).order_by('-created_at')
        return PartnerServiceRequest.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'merchant':
            raise PermissionDenied('Seuls les commerçants peuvent demander un service partenaire.')

        partner_id = self.request.data.get('partnerId')
        if not partner_id:
            raise ValidationError({'partnerId': 'Le partenaire est requis.'})

        serializer.save()


class PartnerServiceRequestAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        service_request = get_object_or_404(PartnerServiceRequest, request_id=request_id)
        if request.user != service_request.partner:
            raise PermissionDenied('Accès refusé.')
        if service_request.statut != 'pending':
            return Response({'detail': 'Cette demande ne peut pas être acceptée.'}, status=status.HTTP_400_BAD_REQUEST)

        service_request.statut = 'accepted'
        service_request.save(update_fields=['statut', 'updated_at'])
        return Response({'success': True, 'message': 'Demande acceptée avec succès.'})


class PartnerServiceRequestCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        service_request = get_object_or_404(PartnerServiceRequest, request_id=request_id)
        if request.user != service_request.partner:
            raise PermissionDenied('Accès refusé.')
        if service_request.statut != 'accepted':
            return Response({'detail': 'Cette demande doit d\'abord être acceptée.'}, status=status.HTTP_400_BAD_REQUEST)

        merchant_wallet = getattr(service_request.merchant, 'wallet', None)
        if not merchant_wallet:
            return Response({'detail': 'Wallet du commerçant introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        
        partner_wallet = getattr(service_request.partner, 'wallet', None)
        if not partner_wallet:
            return Response({'detail': 'Wallet du partenaire introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        
        commission = service_request.commission
        montant_rembourse = service_request.montant_service
        total_a_payer = montant_rembourse + commission

        # Check if merchant can cover it (balance or debt)
        debt_added = False
        if merchant_wallet.balance < total_a_payer:
            if not merchant_wallet.add_pending_debt(total_a_payer):
                return Response(
                    {
                        'detail': 'Dette maximale atteinte. Veuillez recharger votre portefeuille avant de demander de nouveaux services.',
                        'current_debt': merchant_wallet.pending_debt,
                        'max_debt': merchant_wallet.max_allowed_debt
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            debt_added = True

        # Create transaction first, then settle it!
        transaction = Transaction.objects.create(
            merchant=service_request.merchant,
            partner=service_request.partner,
            partner_location=service_request.partner_location,
            customer=service_request.customer,
            montant_achat=Decimal('0'),
            montant_paye=Decimal('0'),
            monnaie_a_rendre=montant_rembourse,
            frais_service=commission,
            statut='validee',
            qr_code=f'SVC-{uuid.uuid4().hex[:12].upper()}',
        )

        CommissionRecord.objects.create(
            transaction=transaction,
            montant_commission=commission,
            type_commission='partenaire',
        )

        # Settle transaction as partner service
        transaction.settle(is_partner_service=True, merchant_wallet=merchant_wallet, partner_wallet=partner_wallet)

        service_request.statut = 'completed'
        service_request.completed_at = timezone.now()
        service_request.save(update_fields=['statut', 'completed_at'])

        return Response(
            {
                'success': True, 
                'message': 'Service partenaire distribué et commission appliquée.',
                'debt_added': debt_added,
                'merchant_current_debt': merchant_wallet.pending_debt
            }
        )


class WalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet = getattr(request.user, 'wallet', None)
        if not wallet:
            return Response({'detail': 'Wallet introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)


class TransactionListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TransactionCreateSerializer
        return TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'merchant':
            return Transaction.objects.filter(merchant=user).order_by('-created_at')
        if user.role == 'partner':
            return Transaction.objects.filter(partner=user).order_by('-created_at')
        if user.role == 'customer':
            return Transaction.objects.filter(customer=user).order_by('-created_at')
        return Transaction.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        
        # Récupérer les coordonnées du merchant
        merchant_lat = user.latitude or 0
        merchant_lng = user.longitude or 0
        
        # Fonction pour calculer la distance (Haversine)
        def haversine_distance(lat1, lng1, lat2, lng2):
            import math
            R = 6371.0  # Earth radius en km
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            d_phi = math.radians(lat2 - lat1)
            d_lambda = math.radians(lng2 - lng1)
            
            a = math.sin(d_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c
        
        # Chercher les locations actives des partenaires actifs
        from .models import Location
        nearby_locations = []
        
        for location in Location.objects.filter(statut='active', partner__statut='actif'):
            distance = haversine_distance(merchant_lat, merchant_lng, location.latitude, location.longitude)
            if distance <= 50:  # Max 50km
                nearby_locations.append((location, distance))
        
        # Trier par distance croissante et prendre les 5 plus proches
        nearby_locations.sort(key=lambda x: x[1])
        top_locations = [loc for loc, _ in nearby_locations[:5]]
        
        # Sélectionner aléatoirement parmi les plus proches
        partner = None
        if top_locations:
            selected_location = random.choice(top_locations)
            transaction = serializer.save(
                merchant=user,
                partner=selected_location.partner,
                partner_location=selected_location
            )
            partner = selected_location.partner
        else:
            # Fallback: partenaire aléatoire si aucune location proche
            partner = User.objects.filter(role='partner', statut='actif').order_by('?').first()
            transaction = serializer.save(merchant=user, partner=partner)

        platform_share = transaction.frais_service * Decimal('0.5')
        merchant_share = transaction.frais_service * Decimal('0.25')
        partner_share = transaction.frais_service * Decimal('0.25')

        CommissionRecord.objects.create(
            transaction=transaction,
            montant_commission=merchant_share,
            type_commission='emetteur',
        )
        CommissionRecord.objects.create(
            transaction=transaction,
            montant_commission=partner_share,
            type_commission='partenaire',
        )
        CommissionRecord.objects.create(
            transaction=transaction,
            montant_commission=platform_share,
            type_commission='plateforme',
        )

        # Si un client est sélectionné, valider immédiatement la transaction
        if transaction.customer:
            transaction.statut = 'validee'
            transaction.save(update_fields=['statut'])
            # La transaction.settle() sera appelée automatiquement par le signal post_save

        return transaction


class TransactionValidateView(APIView):
    """Permet au client, commerçant ou partenaire de valider une transaction en attente"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, transaction_id):
        user = request.user
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        
        # Vérifier que l'utilisateur a le droit de valider cette transaction
        if user.role == 'customer':
            if transaction.customer != user:
                return Response({'detail': 'Vous ne pouvez pas valider cette transaction.'}, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'merchant':
            if transaction.merchant != user:
                return Response({'detail': 'Vous ne pouvez pas valider cette transaction.'}, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'partner':
            if transaction.partner != user:
                return Response({'detail': 'Vous ne pouvez pas valider cette transaction.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'Vous ne pouvez pas valider cette transaction.'}, status=status.HTTP_403_FORBIDDEN)

        if transaction.statut != 'en_attente':
            return Response({'detail': 'Cette transaction ne peut pas être validée.'}, status=status.HTTP_400_BAD_REQUEST)

        transaction.statut = 'validee'
        transaction.save(update_fields=['statut'])
        return Response(TransactionSerializer(transaction).data)


class WalletWithdrawView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        wallet = getattr(request.user, 'wallet', None)
        if not wallet:
            return Response({'detail': 'Wallet introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        if wallet.balance <= 0:
            return Response({'detail': 'Solde insuffisant pour retrait.'}, status=status.HTTP_400_BAD_REQUEST)

        montant_retirer = wallet.balance
        wallet.balance = 0
        wallet.save(update_fields=['balance'])
        return Response({'success': True, 'withdrawn': montant_retirer, 'wallet': WalletSerializer(wallet).data})


class WalletRechargeView(APIView):
    """Recharger le portefeuille du commerçant via FedaPay"""
    permission_classes = [permissions.IsAuthenticated]

    def _build_mock_payment_response(self, request, montant, currency, recharge_id):
        payment_url = request.build_absolute_uri(
            f'/api/wallet/recharge/verify/?recharge_id={recharge_id}&amount={int(montant)}&currency={currency}&user_id={request.user.id}&status=success&mock=true'
        )
        return Response({
            'success': True,
            'paymentUrl': payment_url,
            'reference': f'mock-{recharge_id}',
            'rechargeId': recharge_id,
            'amount': str(montant),
            'status': 'mocked',
            'mock': True,
            'message': 'FedaPay inaccessible. Recharge mock générée en mode debug.',
        })

    def post(self, request):
        # Seuls les commerçants et partenaires peuvent recharger leur portefeuille
        if request.user.role not in ['merchant', 'partner']:
            return Response(
                {'detail': 'Seuls les commerçants et partenaires peuvent recharger leur portefeuille.'},
                status=status.HTTP_403_FORBIDDEN
            )

        amount = request.data.get('amount')
        currency = (request.data.get('currency', 'XOF') or 'XOF').upper()
        
        if amount is None:
            return Response({'detail': 'Le montant est requis.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            montant = Decimal(str(amount))
        except Exception:
            return Response({'detail': 'Montant invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        if montant <= 0:
            return Response({'detail': 'Le montant doit être supérieur à 0.'}, status=status.HTTP_400_BAD_REQUEST)

        if montant > Decimal('1000000'):
            return Response({'detail': 'Le montant dépasse la limite maximale.'}, status=status.HTTP_400_BAD_REQUEST)

        recharge_id = str(uuid.uuid4())
        amount_to_send = int(montant) if currency in ('XOF', 'JPY', 'KRW') else int(montant * 100)
        payload = {
            'amount': amount_to_send,
            'currency': currency,
            'customer': {
                'email': request.user.email,
                'firstname': request.user.prenom or '',
                'lastname': request.user.nom or '',
            },
            'metadata': {
                'recharge_id': recharge_id,
                'user_id': request.user.id,
                'user_role': request.user.role,
                'type': 'wallet_recharge',
            },
            'redirect_url': request.build_absolute_uri('/api/wallet/recharge/verify/'),
        }

        base = (getattr(settings, 'FEDAPAY_API_BASE_URL', '') or '').rstrip('/')
        if not base:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured('FEDAPAY_API_BASE_URL is not configured')
        url = f"{base}/v1/payments"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.FEDAPAY_SECRET_KEY}',
            'X-Public-Key': settings.FEDAPAY_PUBLIC_KEY,
            # Ajouter un User-Agent humain pour passer la barrière Cloudflare
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        }

        use_mock = getattr(settings, 'FEDAPAY_USE_MOCK', False) or getattr(settings, 'DEBUG', False)

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=25) as response:
                raw = response.read()
                text = raw.decode('utf-8', errors='ignore')
                # Detect HTML responses (Cloudflare challenge) and fallback
                if '<!DOCTYPE html>' in text or '<html' in text.lower():
                    logger.error(f"FedaPay returned HTML challenge or page: {text[:300]}")
                    if use_mock:
                        return self._build_mock_payment_response(request, montant, currency, recharge_id)
                    return Response({'detail': 'FedaPay blocked the request (HTML challenge).'}, status=status.HTTP_502_BAD_GATEWAY)
                response_data = json.loads(text)
        except urllib.error.HTTPError as error:
            body = error.read().decode('utf-8') if hasattr(error, 'read') else ''
            logger.error(f"FedaPay error for wallet recharge: {body}")
            if use_mock:
                return self._build_mock_payment_response(request, montant, currency, recharge_id)
            return Response(
                {'detail': 'Impossible de lancer la recharge du portefeuille.', 'error': body},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except urllib.error.URLError as error:
            logger.error(f"Connection error to FedaPay: {str(error)}")
            if use_mock:
                return self._build_mock_payment_response(request, montant, currency, recharge_id)
            return Response(
                {'detail': 'Erreur de connexion à FedaPay.', 'error': str(error)},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as error:
            logger.error(f"Unexpected error while connecting to FedaPay: {str(error)}")
            if use_mock:
                return self._build_mock_payment_response(request, montant, currency, recharge_id)
            return Response(
                {'detail': 'Erreur interne lors de la connexion à FedaPay.', 'error': str(error)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        payment_url = (
            response_data.get('payment_url')
            or response_data.get('url')
            or response_data.get('link')
            or (response_data.get('data') or {}).get('payment_url')
            or (response_data.get('data') or {}).get('url')
            or (response_data.get('data') or {}).get('link')
        )

        if not payment_url:
            logger.error(f"FedaPay response missing payment URL: {response_data}")
            if use_mock:
                return self._build_mock_payment_response(request, montant, currency, recharge_id)
            return Response(
                {
                    'detail': 'Réponse invalide de FedaPay, URL de paiement manquante.',
                    'raw': response_data,
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        logger.info(f"Wallet recharge initiated for user {request.user.id}, amount: {montant}, recharge_id: {recharge_id}")
        
        return Response({
            'success': True,
            'paymentUrl': payment_url,
            'reference': response_data.get('reference') or response_data.get('id'),
            'rechargeId': recharge_id,
            'amount': str(montant),
            'status': response_data.get('status') or 'pending',
        })

    def get(self, request):
        """Récupérer l'état de recharge du portefeuille"""
        wallet = getattr(request.user, 'wallet', None)
        if not wallet:
            return Response(
                {'detail': 'Portefeuille introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'balance': str(wallet.balance),
            'pending_debt': str(wallet.pending_debt),
            'revenus_generes': str(wallet.revenus_generes),
            'created_at': wallet.created_at,
        })


class WalletRechargeVerifyView(APIView):
    """Validation basique de recharge pour les tests locaux."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        recharge_id = request.GET.get('recharge_id')
        amount = request.GET.get('amount')
        currency = request.GET.get('currency', 'XOF')
        status_value = request.GET.get('status', 'success')
        mock_mode = request.GET.get('mock', 'false').lower() in ['1', 'true', 'yes']

        if not recharge_id or not amount:
            return Response({'detail': 'Paramètres manquants pour la validation de recharge.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            montant = Decimal(str(amount))
        except Exception:
            return Response({'detail': 'Montant invalide pour la validation de recharge.'}, status=status.HTTP_400_BAD_REQUEST)

        if status_value != 'success':
            return Response({'success': False, 'message': 'Recharge non complétée.'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if request.user.is_authenticated:
            user = request.user
        else:
            user_id = request.GET.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return Response({'detail': 'Utilisateur introuvable pour la validation de recharge.'}, status=status.HTTP_404_NOT_FOUND)

        if not user:
            if mock_mode:
                return Response({'detail': 'Utilisateur introuvable pour la validation mock.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Authentification requise pour valider la recharge.'}, status=status.HTTP_403_FORBIDDEN)

        wallet = getattr(user, 'wallet', None)
        if not wallet:
            return Response({'detail': 'Portefeuille introuvable pour l’utilisateur.'}, status=status.HTTP_404_NOT_FOUND)

        # Add balance and pay off pending debt first!
        new_balance, debt_paid, remaining_balance = wallet.add_balance_and_pay_debt(montant)
        
        logger.info(f"Mock recharge validated for user {user.id}, amount: {montant}, debt_paid: {debt_paid}, recharge_id: {recharge_id}")

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
        return redirect(f'{frontend_url}/?tab=wallet&recharge_success=true&amount={int(montant)}')

class PaymentInitiateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'XOF')
        transaction_id = request.data.get('transactionId')
        customer_email = request.data.get('email', request.user.email)

        if amount is None:
            return Response({'detail': 'Le montant est requis.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            montant = Decimal(str(amount))
        except Exception:
            return Response({'detail': 'Montant invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        if montant <= 0:
            return Response({'detail': 'Le montant doit être supérieur à 0.'}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            'amount': int(montant * 100),
            'currency': currency,
            'customer': {
                'email': customer_email,
            },
            'metadata': {
                'transaction_id': transaction_id,
                'merchant_id': request.user.id,
            },
            'redirect_url': request.build_absolute_uri('/api/payments/verify/'),
        }

        base = (getattr(settings, 'FEDAPAY_API_BASE_URL', '') or '').rstrip('/')
        if not base:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured('FEDAPAY_API_BASE_URL is not configured')
        url = f"{base}/v1/payments"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.FEDAPAY_SECRET_KEY}',
            'X-Public-Key': settings.FEDAPAY_PUBLIC_KEY,
            'Accept': 'application/json',
            'User-Agent': 'SmartChange/1.0 (+https://smartchangeaimoney.vercel.app)'
        }

        use_mock = getattr(settings, 'FEDAPAY_USE_MOCK', False) or getattr(settings, 'DEBUG', False)

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=25) as response:
                raw = response.read()
                text = raw.decode('utf-8', errors='ignore')
                if '<!DOCTYPE html>' in text or '<html' in text.lower():
                    logger.error(f"FedaPay returned HTML challenge or page: {text[:300]}")
                    if use_mock:
                        return Response({'success': True, 'paymentUrl': request.build_absolute_uri(f'/api/payments/verify/?transactionId={transaction_id}&status=mocked'), 'reference': f'mock-{transaction_id}', 'status': 'mocked', 'mock': True})
                    return Response({'detail': 'FedaPay blocked the request (HTML challenge).'}, status=status.HTTP_502_BAD_GATEWAY)
                response_data = json.loads(text)
        except urllib.error.HTTPError as error:
            body = error.read().decode('utf-8') if hasattr(error, 'read') else ''
            return Response({'detail': 'Impossible de lancer le paiement.', 'error': body}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as error:
            return Response({'detail': 'Erreur de connexion à FedaPay.', 'error': str(error)}, status=status.HTTP_502_BAD_GATEWAY)

        payment_url = response_data.get('payment_url') or response_data.get('url') or response_data.get('link')
        return Response({
            'success': True,
            'paymentUrl': payment_url,
            'reference': response_data.get('reference') or response_data.get('id'),
            'status': response_data.get('status') or 'pending',
            'raw': response_data,
        })


class QRScanView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QRScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference = serializer.validated_data['reference']
        try:
            transaction = Transaction.objects.get(transaction_id=reference)
        except Transaction.DoesNotExist:
            return Response({'status': 'invalid', 'message': 'Référence inconnue.'}, status=status.HTTP_404_NOT_FOUND)

        if transaction.statut == 'validee':
            return Response({'status': 'invalid', 'message': 'Ce QR Code a déjà été utilisé.'})

        expiration = transaction.created_at + timedelta(hours=48)
        if timezone.now() > expiration:
            transaction.statut = 'expiree'
            transaction.save(update_fields=['statut'])
            return Response({'status': 'expired', 'message': 'QR Code expiré.', 'reference': reference, 'montant': transaction.monnaie_a_rendre, 'expiration': expiration})

        risk_score = random.randint(10, 90) if transaction.monnaie_a_rendre > 500 else random.randint(5, 35)
        if risk_score > 70:
            transaction.statut = 'annulee'
            transaction.save(update_fields=['statut'])
            report = FraudReport.objects.create(
                transaction=transaction,
                score_risque=risk_score,
                type_fraude='Comportement suspect',
                description='Le QR Code présente un score de risque élevé.',
            )
            return Response({'status': 'fraud', 'message': 'Fraude détectée.', 'reference': reference, 'montant': transaction.monnaie_a_rendre, 'expiration': expiration, 'isFraud': True})

        transaction.statut = 'validee'
        transaction.save(update_fields=['statut'])
        # The post_save signal will automatically call transaction.settle()
        return Response({'status': 'valid', 'message': 'QR Code valide.', 'reference': reference, 'montant': transaction.monnaie_a_rendre, 'expiration': expiration, 'isFraud': False})


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'admin':
            total = Transaction.objects.count()
            revenue_day = Transaction.objects.filter(created_at__gte=timezone.now() - timedelta(days=1)).aggregate(sum=Sum('frais_service'))['sum'] or 0
            revenue_month = Transaction.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).aggregate(sum=Sum('frais_service'))['sum'] or 0
            clients = User.objects.filter(role='customer').count()
            distributed = Transaction.objects.aggregate(sum=Sum('monnaie_a_rendre'))['sum'] or 0
            recovered = Transaction.objects.filter(statut='validee').aggregate(sum=Sum('monnaie_a_rendre'))['sum'] or 0
        else:
            q = Transaction.objects
            if user.role == 'merchant':
                q = q.filter(merchant=user)
            elif user.role == 'partner':
                q = q.filter(partner=user)
            elif user.role == 'customer':
                q = q.filter(customer=user)
            total = q.count()
            revenue_day = q.filter(created_at__gte=timezone.now() - timedelta(days=1)).aggregate(sum=Sum('frais_service'))['sum'] or 0
            revenue_month = q.filter(created_at__gte=timezone.now() - timedelta(days=30)).aggregate(sum=Sum('frais_service'))['sum'] or 0
            clients = User.objects.filter(role='customer').count() if user.role == 'merchant' else 0
            distributed = q.aggregate(sum=Sum('monnaie_a_rendre'))['sum'] or 0
            recovered = q.filter(statut='validee').aggregate(sum=Sum('monnaie_a_rendre'))['sum'] or 0

        data = {
            'totalTransactions': total,
            'revenusJour': revenue_day,
            'revenusMois': revenue_month,
            'totalClients': clients,
            'monnaieDistribuee': distributed,
            'monnaieRecuperee': recovered,
        }
        serializer = DashboardSerializer(data)
        return Response(serializer.data)


class AdminUsersView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-created_at')


class AdminTransactionsView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all().order_by('-created_at')


class AdminFraudView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = FraudReportSerializer
    queryset = FraudReport.objects.all().order_by('-date_detection')


class AdminCommissionView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = CommissionSerializer
    queryset = CommissionRecord.objects.all().order_by('-date_commission')


class LocationListView(generics.ListCreateAPIView):
    """Lister et créer des locations (CRUD pour partenaires)"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'partner':
            return Location.objects.filter(partner=user).order_by('-updated_at')
        if user.role == 'admin':
            return Location.objects.all().order_by('-updated_at')
        return Location.objects.filter(statut='active').order_by('-updated_at')

    def perform_create(self, serializer):
        user = self.request.user
        # Les partenaires créent leurs propres locations
        if user.role == 'partner':
            serializer.save(partner=user)
        else:
            # Les admins peuvent créer des locations pour n'importe quel partenaire
            serializer.save()


class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détails, mise à jour et suppression d'une location"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationDetailSerializer
    queryset = Location.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'partner':
            return Location.objects.filter(partner=user)
        return Location.objects.all()

    def perform_update(self, serializer):
        # Les partenaires ne peuvent modifier que leurs locations
        user = self.request.user
        location = self.get_object()
        if user.role == 'partner' and location.partner != user:
            return Response({'detail': 'Non autorisé'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()


class LocationStatsView(APIView):
    """Stats détaillées d'une location"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            location = Location.objects.get(pk=pk)
        except Location.DoesNotExist:
            return Response({'detail': 'Location introuvable'}, status=status.HTTP_404_NOT_FOUND)

        # Vérification de permission
        if request.user.role == 'partner' and location.partner != request.user:
            return Response({'detail': 'Non autorisé'}, status=status.HTTP_403_FORBIDDEN)

        # Statistiques
        transactions = location.transactions.all()
        today = timezone.now() - timedelta(days=1)
        month = timezone.now() - timedelta(days=30)

        total_tx = transactions.count()
        tx_today = transactions.filter(created_at__gte=today).count()
        revenue_today = transactions.filter(created_at__gte=today).aggregate(Sum('frais_service'))['frais_service__sum'] or 0
        revenue_month = transactions.filter(created_at__gte=month).aggregate(Sum('frais_service'))['frais_service__sum'] or 0
        validated_tx = transactions.filter(statut='validee').count()
        fraud_tx = transactions.filter(fraud_reports__isnull=False).count()

        taux_validation = (validated_tx / max(total_tx, 1)) * 100
        taux_fraude = (fraud_tx / max(total_tx, 1)) * 100

        return Response({
            'location': LocationDetailSerializer(location, context={'request': request}).data,
            'stats': {
                'totalTransactions': total_tx,
                'transactionsAujourd': tx_today,
                'revenusJour': str(revenue_today),
                'revenusMois': str(revenue_month),
                'transactionsValidees': validated_tx,
                'tauxValidation': round(taux_validation, 2),
                'tauxFraude': round(taux_fraude, 2),
                'fraudDetections': fraud_tx,
            }
        })


class PartnerLocationsView(generics.ListAPIView):
    """Liste les locations d'un partenaire spécifique (pour clients/merchants)"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationSerializer

    def get_queryset(self):
        partner_id = self.kwargs.get('partner_id')
        return Location.objects.filter(partner_id=partner_id, statut='active')


class NearbyLocationsView(APIView):
    """Trouver les locations les plus proches du merchant (avec distance calculée)"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Récupérer les coordonnées du merchant
        lat = request.query_params.get('latitude') or request.user.latitude
        lng = request.query_params.get('longitude') or request.user.longitude
        radius = int(request.query_params.get('radius', 10))  # 10km par défaut

        if not lat or not lng:
            return Response(
                {'detail': 'Coordonnées (latitude, longitude) requises'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response(
                {'detail': 'Latitude et longitude doivent être des nombres'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fonction pour calculer la distance
        import math
        def haversine_distance(lat1, lng1, lat2, lng2):
            R = 6371.0
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            d_phi = math.radians(lat2 - lat1)
            d_lambda = math.radians(lng2 - lng1)
            a = math.sin(d_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        # Récupérer les locations actives
        locations = Location.objects.filter(statut='active', partner__statut='actif')
        nearby = []

        for location in locations:
            if location.latitude and location.longitude:
                distance = haversine_distance(lat, lng, location.latitude, location.longitude)
                if distance <= radius:
                    nearby.append({
                        'location': location,
                        'distance': distance
                    })

        # Trier par distance
        nearby.sort(key=lambda x: x['distance'])

        # Sérialiser les locations avec distance
        serializer = LocationSerializer(
            [item['location'] for item in nearby],
            many=True,
            context={'request': request}
        )

        return Response({
            'count': len(nearby),
            'locations': serializer.data
        })


class SeedTestUsersView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Create test users for development/testing - DEBUG ONLY"""
        # Only allow in DEBUG mode
        if not settings.DEBUG:
            logger.error(f"⚠️ SECURITY: Unauthorized attempt to seed test users from {request.META.get('REMOTE_ADDR')}")
            return Response(
                {'detail': 'Cet endpoint n\'est disponible qu\'en mode développement.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        test_data = [
            {'email': 'merchant@demo.local', 'telephone': '+228 91234567', 'nom': 'Dupont', 'prenom': 'Jean', 'role': 'merchant', 'password': 'Demo123!@'},
            {'email': 'customer@demo.local', 'telephone': '+228 91234568', 'nom': 'Martin', 'prenom': 'Paul', 'role': 'customer', 'password': 'Demo123!@'},
            {'email': 'partner@demo.local', 'telephone': '+228 91234569', 'nom': 'Diouf', 'prenom': 'Fatou', 'role': 'partner', 'password': 'Demo123!@'},
        ]
        
        created = []
        existing = []
        
        for data in test_data:
            user, is_created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['email'].lower(),
                    'telephone': data['telephone'],
                    'nom': data['nom'],
                    'prenom': data['prenom'],
                    'role': data['role'],
                    'is_active': True,
                }
            )
            if is_created:
                user.set_password(data['password'])
                user.save()
                created.append(data['email'])
                logger.info(f"Created test user: {data['email']}")
            else:
                user.set_password(data['password'])
                user.save()
                existing.append(data['email'])
                logger.info(f"Updated test user: {data['email']}")
            # Ensure wallet exists and add test balance for merchant
            wallet, wallet_created = Wallet.objects.get_or_create(user=user)
            if data['role'] == 'merchant' and wallet.balance < 1000:
                wallet.balance = 1000
                wallet.save()
                logger.warning(f"DEBUG: Seeded merchant test user {data['email']} with 1000F (DEBUG MODE ONLY)")
        
        return Response({
            'success': True,
            'message': 'Test users seeded',
            'created': created,
            'updated': existing,
            'test_credentials': [
                {'email': 'merchant@demo.local', 'password': 'Demo123!@', 'role': 'merchant'},
                {'email': 'customer@demo.local', 'password': 'Demo123!@', 'role': 'customer'},
                {'email': 'partner@demo.local', 'password': 'Demo123!@', 'role': 'partner'},
            ]
        })



class DebugAddBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Add test balance to user's wallet (for development ONLY)"""
        # Only allow in DEBUG mode
        if not settings.DEBUG:
            return Response(
                {'detail': 'Cet endpoint n\'est disponible qu\'en mode développement.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        wallet = getattr(request.user, 'wallet', None)
        if not wallet:
            return Response({'detail': 'Wallet introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        from decimal import Decimal
        add_amount = Decimal(request.data.get('amount', 100))
        wallet.balance += add_amount
        wallet.save(update_fields=['balance'])
        serializer = WalletSerializer(wallet)
        logger.warning(f"DEBUG: Added {add_amount}F to user {request.user.id} wallet (DEBUG MODE ONLY)")
        return Response({'success': True, 'message': f'Ajout de {add_amount}F au solde.', 'wallet': serializer.data})
