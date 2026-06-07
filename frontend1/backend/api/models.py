import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


def generate_fraud_id():
    """Generate a unique fraud ID"""
    return uuid.uuid4().hex[:32]


def generate_transaction_id():
    """Generate a unique transaction ID"""
    return str(uuid.uuid4())[:32]


class User(AbstractUser):
    ROLE_CHOICES = [
        ('merchant', 'Commerçant'),
        ('customer', 'Client'),
        ('partner', 'Partenaire'),
        ('admin', 'Administrateur'),
    ]
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('suspendu', 'Suspendu'),
    ]

    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default='merchant')
    statut = models.CharField(max_length=12, choices=STATUT_CHOICES, default='actif')
    nom = models.CharField(max_length=150, blank=True)
    prenom = models.CharField(max_length=150, blank=True)
    nom_boutique = models.CharField(max_length=255, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    horaires = models.CharField(max_length=100, default='9h-18h', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'telephone']

    def __str__(self):
        return f'{self.prenom} {self.nom} ({self.email})'


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Dette en attente (commissions de partenaires non payées)")
    max_allowed_debt = models.DecimalField(max_digits=12, decimal_places=2, default=500, help_text="Dette maximale autorisée")
    revenus_generes = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Wallet {self.user.email}'

    def add_pending_debt(self, amount):
        """Ajoute une dette en attente. Retourne True si ok, False si dépasse la limite."""
        if self.pending_debt + amount > self.max_allowed_debt:
            return False
        self.pending_debt += amount
        self.save(update_fields=['pending_debt'])
        return True

    def add_balance_and_pay_debt(self, recharge_amount):
        """Ajoute du solde, paye d'abord la dette, renvoie (nouveau_solde, dette_payee, solde_restant)"""
        debt_paid = 0
        remaining_balance = recharge_amount
        if self.pending_debt > 0:
            if remaining_balance >= self.pending_debt:
                debt_paid = self.pending_debt
                remaining_balance -= debt_paid
                self.pending_debt = 0
            else:
                debt_paid = remaining_balance
                self.pending_debt -= debt_paid
                remaining_balance = 0
        
        if remaining_balance > 0:
            self.balance += remaining_balance
        
        self.save(update_fields=['balance', 'pending_debt'])
        return self.balance, debt_paid, remaining_balance


class Transaction(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('annulee', 'Annulée'),
        ('expiree', 'Expirée'),
    ]

    transaction_id = models.CharField(max_length=32, unique=True, default=generate_transaction_id)
    merchant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='merchant_transactions')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='customer_transactions')
    partner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner_transactions')
    partner_location = models.ForeignKey('Location', null=True, blank=True, on_delete=models.SET_NULL, related_name='transactions')
    montant_achat = models.DecimalField(max_digits=12, decimal_places=2)
    montant_paye = models.DecimalField(max_digits=12, decimal_places=2)
    monnaie_a_rendre = models.DecimalField(max_digits=12, decimal_places=2)
    frais_service = models.DecimalField(max_digits=12, decimal_places=2)
    statut = models.CharField(max_length=12, choices=STATUT_CHOICES, default='en_attente')
    qr_code = models.CharField(max_length=128, blank=True)
    settled = models.BooleanField(default=False, help_text="Indique si la transaction a été réglée (portefeuilles mis à jour)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id

    def settle(self, is_partner_service: bool = False, merchant_wallet = None, partner_wallet = None):
        """
        Règlement de la transaction:
        1. Ajouter monnaie_a_rendre au solde du client
        2. Distribution des frais de service entre commerçant, partenaire et plateforme
        3. Si is_partner_service=True: traiter comme demande de service partenaire
        """
        import logging
        from decimal import Decimal
        logger = logging.getLogger(__name__)

        if self.settled or self.statut != 'validee':
            return

        merchant_wallet = merchant_wallet or getattr(self.merchant, 'wallet', None)
        partner_wallet = partner_wallet or (getattr(self.partner, 'wallet', None) if self.partner else None)
        client_wallet = getattr(self.customer, 'wallet', None) if self.customer else None
        
        # 1. Ajouter le monnaie à distribuer au solde du client (PRIORITAIRE!)
        if client_wallet:
            client_wallet.balance += self.monnaie_a_rendre
            client_wallet.save(update_fields=['balance'])
            logger.info(f"Client {self.customer.id} received {self.monnaie_a_rendre} in wallet from transaction {self.transaction_id}")

        if is_partner_service:
            # Traitement pour demande de service partenaire
            total_a_payer = self.monnaie_a_rendre + self.frais_service
            
            if partner_wallet:
                partner_wallet.balance += total_a_payer
                partner_wallet.revenus_generes += self.frais_service
                partner_wallet.save(update_fields=['balance', 'revenus_generes'])
                logger.info(f"Partner {self.partner.id} settled partner service transaction {self.transaction_id}: "
                           f"received {total_a_payer}, balance now {partner_wallet.balance}")

            if merchant_wallet:
                if merchant_wallet.balance >= total_a_payer:
                    merchant_wallet.balance -= total_a_payer
                else:
                    merchant_wallet.add_pending_debt(total_a_payer)
                merchant_wallet.save(update_fields=['balance', 'pending_debt'])
                logger.info(f"Merchant {self.merchant.id} settled partner service transaction {self.transaction_id}: "
                           f"deducted {total_a_payer}, balance now {merchant_wallet.balance}")
        else:
            # Traitement normal
            merchant_net = max(self.monnaie_a_rendre - (self.frais_service * Decimal('0.5')), Decimal('0'))
            partner_share = self.frais_service * Decimal('0.25')
            merchant_service_fee = self.frais_service * Decimal('0.25')

            if merchant_wallet:
                # Ajouter la part du commerçant au solde
                merchant_wallet.balance += merchant_net
                
                # Prélever automatiquement les frais de service du solde
                if merchant_wallet.balance >= merchant_service_fee:
                    merchant_wallet.balance -= merchant_service_fee
                else:
                    merchant_wallet.add_pending_debt(merchant_service_fee)
                
                merchant_wallet.revenus_generes += merchant_service_fee
                merchant_wallet.save(update_fields=['balance', 'pending_debt', 'revenus_generes'])
                
                logger.info(f"Merchant {self.merchant.id} settled transaction {self.transaction_id}: "
                           f"received {merchant_net}, deducted {merchant_service_fee}, balance now {merchant_wallet.balance}")

            if partner_wallet:
                partner_wallet.balance += partner_share
                partner_wallet.revenus_generes += partner_share
                partner_wallet.save(update_fields=['balance', 'revenus_generes'])
                
                logger.info(f"Partner {self.partner.id} settled transaction {self.transaction_id}: "
                           f"received {partner_share}, balance now {partner_wallet.balance}")

        self.settled = True
        self.save(update_fields=['settled'])


class QRCodeRecord(models.Model):
    reference = models.CharField(max_length=64, unique=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='qr_code_record')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    is_fraud = models.BooleanField(default=False)

    def __str__(self):
        return self.reference


class FraudReport(models.Model):
    fraud_id = models.CharField(max_length=32, unique=True, default=generate_fraud_id)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='fraud_reports')
    score_risque = models.PositiveSmallIntegerField()
    type_fraude = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_detection = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fraud_id


class CommissionRecord(models.Model):
    COMMISSION_TYPE_CHOICES = [
        ('plateforme', 'Plateforme'),
        ('emetteur', 'Émetteur'),
        ('partenaire', 'Partenaire'),
    ]
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='commissions')
    montant_commission = models.DecimalField(max_digits=12, decimal_places=2)
    type_commission = models.CharField(max_length=12, choices=COMMISSION_TYPE_CHOICES)
    date_commission = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.type_commission} - {self.montant_commission}'


class Location(models.Model):
    """Représente une succursale/boutique d'un partenaire"""
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspendue'),
    ]
    
    partner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='locations')
    nom = models.CharField(max_length=255, help_text="Nom de la boutique (ex: Boutique Centre-Ville)")
    adresse = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    telephone = models.CharField(max_length=20, blank=True)
    horaires = models.CharField(max_length=100, default='9h-18h', blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='active')
    
    # Métrics
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Solde par location")
    revenus_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    nombre_transactions = models.PositiveIntegerField(default=0)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['partner', 'adresse']]
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['partner', 'statut']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.partner.nom_boutique} - {self.nom}"


class PartnerServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('completed', 'Complétée'),
        ('cancelled', 'Annulée'),
    ]

    request_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    merchant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    partner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='partner_service_requests')
    partner_location = models.ForeignKey('Location', null=True, blank=True, on_delete=models.SET_NULL, related_name='service_requests')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='customer_service_requests')
    client_identifier = models.CharField(max_length=255, blank=True)
    montant_service = models.DecimalField(max_digits=12, decimal_places=2, default=25)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=25)
    statut = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    note = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['merchant', 'partner', 'statut']),
            models.Index(fields=['request_id']),
        ]

    def __str__(self):
        return f"Service {self.request_id} - {self.merchant.email} → {self.partner.email}"


@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
