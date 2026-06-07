# 🎯 Système de Recharge Portefeuille avec Déduction Automatique

## Aperçu

Système complet permettant aux commerçants de recharger leur portefeuille via Fadapay, avec déduction automatique des frais après chaque transaction QR.

## Architecture

### Backend (Django REST)

#### Nouvelle Vue: `WalletRechargeView`
**Fichier:** `api/views.py`

```python
class WalletRechargeView(APIView):
    """Recharger le portefeuille du commerçant via Fadapay"""
```

**Endpoints:**
- **POST** `/api/wallet/recharge/` - Initier une recharge
- **GET** `/api/wallet/recharge/` - Consulter l'état du portefeuille

**Requête POST:**
```json
{
  "amount": 50000,
  "currency": "XOF"
}
```

**Réponse:**
```json
{
  "success": true,
  "paymentUrl": "https://sandbox.fadadey.com/pay/...",
  "reference": "ref_xxxxx",
  "rechargeId": "uuid-xxxxx",
  "amount": "50000",
  "status": "pending"
}
```

#### Modification: `_settle_transaction()`
**Fichier:** `api/views.py` dans la classe `QRScanView`

Le flux de règlement est maintenant:
1. **Distribution:** Ajouter le monnaie au solde du commerçant
2. **Déduction:** Prélever les frais automatiquement du solde
3. **Logging:** Traçabilité complète des opérations

```python
def _settle_transaction(self, transaction):
    """
    Règlement de la transaction:
    1. Distribution du monnaie au portefeuille du commerçant
    2. Prélèvement automatique des frais de service
    """
    if merchant_wallet:
        # 1. Ajouter le monnaie
        merchant_wallet.balance += merchant_net
        
        # 2. Prélever les frais
        merchant_wallet.balance -= merchant_service_fee
        
        # 3. Mettre à jour les stats
        merchant_wallet.save()
```

### Frontend (React/TypeScript)

#### 1. API Service
**Fichier:** `src/api/index.ts`

```typescript
export async function rechargeWallet(amount: number, currency: string = 'XOF') {
  return apiRequest<{
    success: boolean;
    paymentUrl?: string;
    reference?: string;
    rechargeId?: string;
    amount?: string;
    status?: string;
  }>('/api/wallet/recharge/', {
    method: 'POST',
    body: JSON.stringify({ amount, currency }),
  });
}
```

#### 2. Composant Modal
**Fichier:** `src/components/WalletRechargeModal.tsx`

Modal d'interface utilisateur avec:
- ✅ Affichage du solde actuel
- ✅ Montants rapides (10K, 25K, 50K, 100K F)
- ✅ Input personnalisé avec validation
- ✅ Validation min (1,000 F) / max (1,000,000 F)
- ✅ Gestion des états (loading, error, success)
- ✅ Redirection automatique vers Fadapay

```tsx
<WalletRechargeModal
  isOpen={rechargeModalOpen}
  onClose={() => setRechargeModalOpen(false)}
  currentBalance={wallet?.balance ?? 0}
  userRole="merchant"
/>
```

#### 3. Integration dans WalletPage
**Fichier:** `src/pages/WalletPage.tsx`

```tsx
<button 
  onClick={() => setRechargeModalOpen(true)}
  style={{ display: 'flex', alignItems: 'center', gap: 6 }}
>
  <Zap size={14} /> Recharger
</button>
```

#### 4. Page Démo Interactive
**Fichier:** `src/pages/WalletDemoPage.tsx`

- 📊 Démonstration complète du flux
- 📝 Documentation API intégrée
- 🎮 Composant interactif de démo
- 📈 Visualisation du parcours utilisateur

## Flux Complet

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMMERÇANT CLIQUE "RECHARGER"                │
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MODAL DE RECHARGE S'AFFICHE                    │
│  - Solde actuel: 50,000 F                                       │
│  - Montants rapides disponibles                                 │
│  - Input de montant personnalisé                                │
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              COMMERÇANT SÉLECTIONNE 50,000 F                     │
│              CLIQUE "CONTINUER VERS FADAPAY"                   │
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│           POST /api/wallet/recharge/                            │
│  - Backend crée ID de recharge unique                           │
│  - Appel Fadapay API                                            │
│  - Retourne paymentUrl et rechargeId                            │
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│        FRONTEND REDIRIGE VERS FADAPAY (window.location.href)    │
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│    COMMERÇANT EFFECTUE LE PAIEMENT CHEZ FADAPAY                │
│  (Carte bancaire, Mobile money, etc.)                          │
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│      WEBHOOK/CALLBACK: PORTEFEUILLE EST CRÉDITÉ                 │
│  Solde: 50,000 F → 100,000 F (+50,000 F)                       │
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              CLIENT SCANNE LE QR CODE                           │
│  → Montant à distribuer: 10,000 F                               │
│  → Frais service: 500 F (5% commission)                         │
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│         COMMERÇANT DISTRIBUE 10,000 F AU CLIENT                 │
│  Solde intermédiaire: 110,000 F (100K + 10K)                   │
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│      FRAIS SONT PRÉLEVÉS AUTOMATIQUEMENT                        │
│  - Solde avant: 110,000 F                                       │
│  - Frais (25%): 500 F                                           │
│  - Solde final: 109,500 F ✓                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Exemple Pratique

### Scénario 1: Recharge Simple
```
État initial:     50,000 F

Recharge:         +50,000 F (via Fadapay)
Nouveau solde:    100,000 F ✓
```

### Scénario 2: Transaction Complète
```
Solde actuel:     100,000 F

Distribution:     +10,000 F (client reçoit)
Solde interim:    110,000 F

Frais (25%):      -500 F (prélevé automatiquement)
Solde final:      109,500 F ✓

Breakdown:
├── Plateforme (50%): 250 F
├── Commerçant (25%): 250 F (déjà déduit)
└── Partenaire (25%): 250 F
```

## Fichiers Modifiés

### Backend
- ✅ `backend/api/views.py` - Ajout `WalletRechargeView` + modification `_settle_transaction()`
- ✅ `backend/api/urls.py` - Ajout route `/api/wallet/recharge/`

### Frontend
- ✅ `frontend/src/api/index.ts` - Ajout fonction `rechargeWallet()`
- ✅ `frontend/src/pages/WalletPage.tsx` - Intégration du modal
- ✅ `frontend/src/components/WalletRechargeModal.tsx` - Nouveau composant (créé)
- ✅ `frontend/src/components/WalletRechargeDemo.tsx` - Composant de démo (créé)
- ✅ `frontend/src/pages/WalletDemoPage.tsx` - Page de démonstration (créé)
- ✅ `frontend/src/components/TestSection.tsx` - Composant utilitaire (créé)

## Installation et Test

### 1. Backend
```bash
cd frontend1/backend
python manage.py runserver
```

### 2. Frontend
```bash
cd frontend1/frontend1
npm run dev
```

### 3. Accédez à la démo
```
http://localhost:5173/demo/wallet
```

## Sécurité

✅ Validation des montants (min/max)
✅ Authentification Bearer token requise
✅ Vérification du rôle utilisateur (merchant/partner uniquement)
✅ Logging complet de toutes les transactions
✅ Gestion d'erreur robuste
✅ Timeouts sur les appels API (25s)

## Points Clés

1. **Déduction Automatique**: Les frais sont prélevés automatiquement après chaque QR scan
2. **Fadapay Intégré**: Utilise le test de Fadapay déjà en place
3. **Solde en Temps Réel**: Affichage du solde actualisé après chaque opération
4. **Historique**: Toutes les opérations sont enregistrées et traçables
5. **Validation**: Min 1,000 F, Max 1,000,000 F

## Support

Pour les questions ou problèmes:
1. Consultez `WalletDemoPage.tsx` pour la documentation API
2. Vérifiez les logs serveur pour les erreurs Fadapay
3. Testez d'abord avec les montants rapides (10K, 25K, 50K, 100K)
