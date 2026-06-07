#!/usr/bin/env python
"""
Test script for transaction settlement via the new settle() method and signals
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Wallet, Transaction

User = get_user_model()


def test_transaction_settlement():
    print("="*80)
    print("🧪 TEST: Transaction Settlement")
    print("="*80)

    # 1. Clean up test users
    print("\n1️⃣  Cleaning up test users...")
    User.objects.filter(email__contains="test_settle").delete()

    # 2. Create test users
    print("\n2️⃣  Creating test users...")
    merchant = User.objects.create_user(
        email='merchant_test_settle@test.local',
        username='merchant_test_settle',
        telephone='+228 99999991',
        password='TestPass123!',
        role='merchant',
        nom='Test',
        prenom='Merchant',
    )
    print(f"   ✅ Merchant created: {merchant.email}")

    partner = User.objects.create_user(
        email='partner_test_settle@test.local',
        username='partner_test_settle',
        telephone='+228 99999992',
        password='TestPass123!',
        role='partner',
        nom='Test',
        prenom='Partner',
    )
    print(f"   ✅ Partner created: {partner.email}")

    customer = User.objects.create_user(
        email='customer_test_settle@test.local',
        username='customer_test_settle',
        telephone='+228 99999993',
        password='TestPass123!',
        role='customer',
        nom='Test',
        prenom='Customer',
    )
    print(f"   ✅ Customer created: {customer.email}")

    # 3. Get wallets
    print("\n3️⃣  Getting wallets...")
    merchant_wallet = Wallet.objects.get(user=merchant)
    partner_wallet = Wallet.objects.get(user=partner)
    customer_wallet = Wallet.objects.get(user=customer)
    print(f"   - Merchant balance before: {merchant_wallet.balance}")
    print(f"   - Partner balance before: {partner_wallet.balance}")
    print(f"   - Customer balance before: {customer_wallet.balance}")

    # 4. Create transaction and mark as validee
    print("\n4️⃣  Creating and validating transaction...")
    tx = Transaction.objects.create(
        merchant=merchant,
        partner=partner,
        customer=customer,
        montant_achat=Decimal('1000'),
        montant_paye=Decimal('1500'),
        monnaie_a_rendre=Decimal('500'),
        frais_service=Decimal('20'),
        statut='en_attente',
        settled=False
    )
    print(f"   ✅ Transaction created: {tx.transaction_id}")

    # 5. Mark transaction as validee (this should trigger the signal!)
    tx.statut = 'validee'
    tx.save()
    print("   ✅ Transaction marked as 'validee'")

    # 6. Refresh wallets and check results
    print("\n5️⃣  Checking results...")
    merchant_wallet.refresh_from_db()
    partner_wallet.refresh_from_db()
    customer_wallet.refresh_from_db()
    tx.refresh_from_db()

    print(f"   - Merchant balance after: {merchant_wallet.balance}")
    print(f"   - Partner balance after: {partner_wallet.balance}")
    print(f"   - Customer balance after: {customer_wallet.balance}")
    print(f"   - Transaction settled: {tx.settled}")

    # Expected calculations
    merchant_net = max(tx.monnaie_a_rendre - (tx.frais_service * Decimal('0.5')), Decimal('0'))
    merchant_fee = tx.frais_service * Decimal('0.25')
    partner_share = tx.frais_service * Decimal('0.25')

    expected_merchant_balance = merchant_net - merchant_fee
    expected_partner_balance = partner_share
    expected_customer_balance = tx.monnaie_a_rendre

    print(f"\n   Expected:")
    print(f"   - Merchant: {expected_merchant_balance}")
    print(f"   - Partner: {expected_partner_balance}")
    print(f"   - Customer: {expected_customer_balance}")

    all_ok = True
    if merchant_wallet.balance == expected_merchant_balance:
        print("   ✅ Merchant balance correct!")
    else:
        print(f"   ❌ Merchant balance wrong: got {merchant_wallet.balance}, expected {expected_merchant_balance}")
        all_ok = False

    if partner_wallet.balance == expected_partner_balance:
        print("   ✅ Partner balance correct!")
    else:
        print(f"   ❌ Partner balance wrong: got {partner_wallet.balance}, expected {expected_partner_balance}")
        all_ok = False

    if customer_wallet.balance == expected_customer_balance:
        print("   ✅ Customer balance correct!")
    else:
        print(f"   ❌ Customer balance wrong: got {customer_wallet.balance}, expected {expected_customer_balance}")
        all_ok = False

    if tx.settled:
        print("   ✅ Transaction marked as settled!")
    else:
        print("   ❌ Transaction not marked as settled!")
        all_ok = False

    print("\n" + "="*80)
    if all_ok:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("="*80)


if __name__ == '__main__':
    test_transaction_settlement()
