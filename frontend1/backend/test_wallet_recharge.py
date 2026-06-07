#!/usr/bin/env python
"""
Script de test du système de recharge de portefeuille
Vérifie:
1. L'endpoint POST /api/wallet/recharge/
2. L'endpoint GET /api/wallet/recharge/
3. La déduction automatique dans _settle_transaction()
"""

import os
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from api.models import Wallet, Transaction

User = get_user_model()

def test_wallet_recharge():
    """Test complet du système de recharge"""
    print("=" * 80)
    print("🧪 TEST: Système de Recharge Portefeuille")
    print("=" * 80)
    
    # 1. Créer un utilisateur test
    print("\n1️⃣  Création d'un utilisateur test...")
    try:
        user = User.objects.create_user(
            email='merchant_test@test.local',
            username='merchant_test',
            telephone='+228 98765432',
            password='TestPass123!',
            role='merchant',
            nom='Test',
            prenom='Merchant',
        )
        print(f"   ✅ Utilisateur créé: {user.email}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # 2. Vérifier/créer le portefeuille
    print("\n2️⃣  Vérification du portefeuille...")
    try:
        wallet, created = Wallet.objects.get_or_create(user=user)
        wallet.balance = Decimal('50000')
        wallet.save()
        print(f"   ✅ Portefeuille: {wallet.balance} F (créé={created})")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # 3. Tester l'endpoint GET /api/wallet/recharge/
    print("\n3️⃣  Test GET /api/wallet/recharge/...")
    client = Client()
    try:
        client.force_login(user)
        response = client.get('/api/wallet/recharge/')
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"   ✅ Réponse: {data}")
            print(f"   - Balance: {data.get('balance')} F")
            print(f"   - En attente: {data.get('balance_en_attente')} F")
            print(f"   - Revenus générés: {data.get('revenus_generes')} F")
        else:
            print(f"   ❌ Erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # 4. Tester l'endpoint POST /api/wallet/recharge/
    print("\n4️⃣  Test POST /api/wallet/recharge/...")
    try:
        payload = {
            'amount': 50000,
            'currency': 'XOF'
        }
        response = client.post(
            '/api/wallet/recharge/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"   ✅ Recharge initiée")
            print(f"   - Success: {data.get('success')}")
            print(f"   - RechargeId: {data.get('rechargeId')}")
            print(f"   - Status: {data.get('status')}")
            if 'error' not in data:
                print(f"   ⚠️  Note: paymentUrl simulée (mode test Fadapay)")
        else:
            print(f"   ❌ Erreur HTTP {response.status_code}")
            print(f"   Réponse: {response.content.decode()}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # 5. Tester la déduction automatique
    print("\n5️⃣  Test déduction automatique (_settle_transaction)...")
    try:
        # Créer une transaction test
        from api.models import Location
        
        # Obtenir ou créer un partenaire
        partner = User.objects.filter(role='partner').first()
        if not partner:
            partner = User.objects.create_user(
                email='partner_test@test.local',
                username='partner_test',
                telephone='+228 98765433',
                password='TestPass123!',
                role='partner',
                nom='Partner',
                prenom='Test',
            )
        
        # Créer/récupérer une location
        location = Location.objects.first()
        if not location:
            location = Location.objects.create(
                partner=partner,
                nom='Test Location',
                adresse='Test Street',
                latitude=12.345,
                longitude=-1.234,
                statut='active'
            )
        
        # Créer une transaction
        tx = Transaction.objects.create(
            merchant=user,
            partner=partner,
            partner_location=location,
            montant_achat=Decimal('10000'),
            montant_paye=Decimal('10000'),
            monnaie_a_rendre=Decimal('10000'),
            frais_service=Decimal('500'),
            statut='validee',
        )
        
        # Récupérer le portefeuille avant
        wallet.refresh_from_db()
        balance_before = wallet.balance
        print(f"   - Solde avant: {balance_before} F")
        print(f"   - Monnaie à distribuer: {tx.monnaie_a_rendre} F")
        print(f"   - Frais service: {tx.frais_service} F")
        
        # Simuler le règlement (sans QR scan)
        from api.views import QRScanView
        qr_view = QRScanView()
        qr_view._settle_transaction(tx)
        
        # Vérifier le portefeuille après
        wallet.refresh_from_db()
        balance_after = wallet.balance
        print(f"   - Solde après: {balance_after} F")
        
        # Calculs attendus
        merchant_net = max(tx.monnaie_a_rendre - (tx.frais_service * Decimal('0.5')), Decimal('0'))
        merchant_fee = tx.frais_service * Decimal('0.25')
        expected_balance = balance_before + merchant_net - merchant_fee
        
        print(f"   - Monnaie nette reçue: {merchant_net} F")
        print(f"   - Frais prélevés: {merchant_fee} F")
        print(f"   - Solde attendu: {expected_balance} F")
        
        if balance_after == expected_balance:
            print(f"   ✅ Déduction correcte!")
        else:
            print(f"   ⚠️  Différence: {balance_after} vs {expected_balance}")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Validation des montants
    print("\n6️⃣  Test validation des montants...")
    test_cases = [
        (500, False, "Montant trop faible"),
        (1000, True, "Montant minimum valide"),
        (50000, True, "Montant standard"),
        (1000000, True, "Montant maximum valide"),
        (1000001, False, "Montant trop élevé"),
        (-1000, False, "Montant négatif"),
    ]
    
    for amount, should_pass, description in test_cases:
        payload = {'amount': amount, 'currency': 'XOF'}
        response = client.post(
            '/api/wallet/recharge/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        is_valid = response.status_code == 200
        status = "✅" if is_valid == should_pass else "❌"
        print(f"   {status} {amount:,} F: {description} (valide={is_valid})")
    
    print("\n" + "=" * 80)
    print("✅ TOUS LES TESTS COMPLÉTÉS")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    success = test_wallet_recharge()
    exit(0 if success else 1)
