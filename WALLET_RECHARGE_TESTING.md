# 🚀 Guide de Test Frontend - Système de Recharge Portefeuille

## Démarrage Rapide

### 1. Lancez le Backend
```bash
cd c:\Hackathon\frontend1\backend
python manage.py runserver
```
Vérifiez: `http://localhost:8000/api/`

### 2. Lancez le Frontend
```bash
cd c:\Hackathon\frontend1\frontend1
npm run dev
```
Vérifiez: `http://localhost:5173`

## 🧪 Scénarios de Test

### Scénario 1: Recharge Simple via Modal

**Étapes:**
1. Connectez-vous avec un compte commerçant
   - Email: `merchant@demo.local`
   - Password: `Demo123!@`

2. Naviguez vers **Portefeuille**

3. Cliquez sur le bouton **Recharger** (avec icône ⚡)

4. Dans le modal:
   - ✅ Vérifiez le solde actuel
   - ✅ Cliquez sur "50,000 F" (montant rapide)
   - ✅ Cliquez "Continuer vers Fadapay"

5. **Résultat attendu:**
   - ✅ Le modal affiche "Recharge initiée"
   - ✅ Une URL Fadapay s'ouvre (test)
   - ✅ RechargeId est affiché (pour suivi)

**Points à vérifier:**
- [ ] Le montant s'affiche bien dans le modal
- [ ] Les boutons rapides (10K, 25K, 50K, 100K) fonctionnent
- [ ] Le bouton "Continuer vers Fadapay" est actif
- [ ] Les messages d'erreur s'affichent pour montants invalides

### Scénario 2: Validation des Montants

**Tester chaque cas:**

| Montant | Résultat | Erreur Attendue |
|---------|----------|-----------------|
| (vide) | ❌ Bouton désactivé | "Veuillez entrer un montant" |
| 500 | ❌ Erreur | "minimum est 1,000 XOF" |
| 1,000 | ✅ OK | - |
| 50,000 | ✅ OK | - |
| 1,000,000 | ✅ OK | - |
| 1,000,001 | ❌ Erreur | "maximum est 1,000,000 XOF" |
| -5,000 | ❌ Erreur | "doit être supérieur à 0" |

### Scénario 3: Déduction Automatique

**Préparation:**
1. Connectez-vous en tant que commerçant
2. Assurez-vous d'avoir un solde de test (ex: 100,000 F)

**Étapes:**
1. Allez à **Tableau de bord**
2. Créez une **nouvelle transaction** QR
   - Montant achat: 10,000 F
   - Montant payé: 10,000 F

3. Visez votre **caméra** pour scanner
   - Aller à **Scan QR Code**
   - Utilisez l'ID de transaction généré

4. **Après le scan:**
   - [ ] La transaction devient "Validée"
   - [ ] Le portefeuille est mis à jour
   - [ ] Les frais sont déduits automatiquement

**Calcul attendu:**
```
Avant:     100,000 F
+ Reçu:     +10,000 F (distribution)
= Interim:  110,000 F

- Frais:     -500 F (25% commission)
= Final:    109,500 F
```

### Scénario 4: Historique des Opérations

**Vérifications:**
1. Ouvrez la page **Portefeuille**
2. Vérifiez l'**Historique des opérations**
   - [ ] Les recharges apparaissent
   - [ ] Les distributions apparaissent
   - [ ] Les frais apparaissent
   - [ ] Les dates sont correctes

### Scénario 5: Page Démo Interactive

**Pour comprendre le flux complet:**
1. Naviguez à `/demo/wallet` (si défini)
2. Ou cherchez **Wallet Demo Page**
3. **Interactions disponibles:**
   - 📖 Parcourez les 8 étapes du flux
   - 👀 Visualisez le changement de solde en temps réel
   - 📊 Consultez le graphique de solde
   - 📚 Lisez la documentation API intégrée

## 🔍 Tests Avancés

### Test 1: Montants Limites
```javascript
// Test avec min
POST /api/wallet/recharge/
{ "amount": 1000, "currency": "XOF" }
// Attendu: Succès ✓

// Test avec max
POST /api/wallet/recharge/
{ "amount": 1000000, "currency": "XOF" }
// Attendu: Succès ✓

// Test au-delà du max
POST /api/wallet/recharge/
{ "amount": 1000001, "currency": "XOF" }
// Attendu: Erreur "montant dépasse la limite"
```

### Test 2: Flux Authentification

**Avec token expiré:**
1. Ouvrez le **DevTools** (F12)
2. Allez à **Application** → **LocalStorage**
3. Supprimez le token `smartchange_access_token`
4. Essayez de recharger
5. **Attendu:** Redirection vers la connexion

### Test 3: Erreurs Réseau

**Simuler une erreur Fadapay:**
1. Dans le DevTools, allez à **Network**
2. Filtrez les requêtes à `/api/wallet/recharge/`
3. Throttlez la connexion (Slow 3G)
4. Cliquez "Recharger"
5. **Attendu:** Le modal affiche un timeout ou message d'erreur

### Test 4: États Multiples

**Dans le modal, testez les états:**
- [ ] État initial (input vide)
- [ ] État avec montant (bouton actif)
- [ ] État loading (spinner, bouttons désactivés)
- [ ] État succès (message + ID recharge)
- [ ] État erreur (message d'erreur en rouge)

## 📊 Vérification des Données

### Check 1: Balance en Base de Données
```bash
# Depuis Django shell:
python manage.py shell
>>> from api.models import Wallet
>>> user = User.objects.get(email='merchant@demo.local')
>>> wallet = user.wallet
>>> print(f"Balance: {wallet.balance} F")
>>> print(f"En attente: {wallet.balance_en_attente} F")
>>> print(f"Revenus: {wallet.revenus_generes} F")
```

### Check 2: Historique des Transactions
```bash
python manage.py shell
>>> from api.models import Transaction
>>> txs = Transaction.objects.filter(merchant=user).order_by('-created_at')[:5]
>>> for tx in txs:
...     print(f"{tx.transaction_id}: {tx.statut} - {tx.monnaie_a_rendre} F")
```

### Check 3: Commissions Appliquées
```bash
python manage.py shell
>>> from api.models import CommissionRecord
>>> commissions = CommissionRecord.objects.filter(transaction=tx)
>>> for c in commissions:
...     print(f"{c.type_commission}: {c.montant_commission} F")
```

## 🐛 Dépannage

### Problème: Le modal ne s'ouvre pas
**Solution:**
- Vérifiez que `WalletRechargeModal` est importé dans `WalletPage.tsx`
- Vérifiez que le bouton "Recharger" a `onClick={() => setRechargeModalOpen(true)}`
- Vérifiez la console (F12) pour les erreurs JavaScript

### Problème: Les montants rapides ne fonctionnent pas
**Solution:**
- Vérifiez que `handleQuickAmount()` met à jour `amount` state
- Vérifiez que l'input a `value={amount}`

### Problème: Erreur "Authentification requise"
**Solution:**
- Connectez-vous d'abord
- Vérifiez que le token est dans LocalStorage
- Refreshez la page (Ctrl+Shift+R)

### Problème: Fadapay retourne une erreur
**Solution:**
- Vérifiez les variables d'environnement:
  ```bash
  echo $FADADEY_API_BASE_URL
  echo $FADADEY_SECRET_KEY
  echo $FADADEY_PUBLIC_KEY
  ```
- Vérifiez que le montant est en cents (50000 → 5000000 centimes)
- Consultez les logs du serveur Django

### Problème: Les frais ne sont pas déduits
**Solution:**
- Vérifiez que la transaction a `statut='validee'`
- Vérifiez que `_settle_transaction()` est appelé dans `QRScanView`
- Vérifiez les logs pour les exceptions

## 📈 Métriques à Monitorer

Pendant vos tests, observez:

| Métrique | Avant | Après Recharge | Après QR |
|----------|-------|-----------------|----------|
| Balance | 50,000 F | 100,000 F | 109,500 F |
| Balance en attente | 0 F | 0 F | 0 F |
| Revenus générés | 0 F | 0 F | +500 F |
| Commissions | 0 | 0 | 3 (plat., commerçant, partenaire) |

## ✅ Checklist de Validation

Avant de déployer, confirmez:

- [ ] Modal s'ouvre et se ferme correctement
- [ ] Montants rapides fonctionnent (10K, 25K, 50K, 100K)
- [ ] Input personnalisé valide min/max
- [ ] Appel API POST vers `/api/wallet/recharge/` réussit
- [ ] paymentUrl est retournée et utilisable
- [ ] rechargeId est généré et affiché
- [ ] Frais sont déduits après QR scan
- [ ] Historique affiche les opérations
- [ ] Solde affiche le montant final correct
- [ ] Pas d'erreurs en console (F12)
- [ ] Pas d'erreurs en backend (terminal Django)
- [ ] Les états de chargement s'affichent
- [ ] Messages d'erreur s'affichent en cas de problème

## 🎓 Documentation Supplémentaire

Consultez:
- `/WALLET_RECHARGE_README.md` - Documentation technique complète
- `WalletDemoPage.tsx` - Page de démonstration interactive
- `WalletRechargeModal.tsx` - Code du composant modal
- `views.py` - Code de l'endpoint backend
