# 🚀 QUICK START - Système de Recharge Portefeuille

## ⚡ 5 Minutes pour Démarrer

### Étape 1: Ouvrir Deux Terminaux

**Terminal 1 (Backend):**
```bash
cd c:\Hackathon\frontend1\backend
python manage.py runserver
```

**Terminal 2 (Frontend):**
```bash
cd c:\Hackathon\frontend1\frontend1
npm run dev
```

### Étape 2: Accéder à l'Application

Ouvrir dans le navigateur:
```
http://localhost:5173
```

### Étape 3: Se Connecter

```
Email:    merchant@demo.local
Password: Demo123!@
```

### Étape 4: Tester la Recharge

1. Cliquer sur **Portefeuille** (menu)
2. Cliquer sur **Recharger ⚡**
3. Sélectionner **50,000 F**
4. Cliquer **Continuer vers Fadapay**
5. Voir le solde passer de **50K → 100K** ✓

---

## 📋 Checklist Rapide

- [ ] Backend démarré (Terminal 1)
- [ ] Frontend démarré (Terminal 2)
- [ ] Application accessible: http://localhost:5173
- [ ] Connecté avec merchant@demo.local
- [ ] Page Portefeuille visible
- [ ] Bouton "Recharger ⚡" visible
- [ ] Modal s'ouvre au clic
- [ ] Montants rapides affichés
- [ ] Recharge testée avec succès ✓

---

## 🔍 Test Complet (10 minutes)

### Scénario 1: Recharge Simple
```
1. Login: merchant@demo.local / Demo123!@
2. Aller à: Portefeuille
3. Cliquer: Recharger ⚡
4. Sélectionner: 50,000 F
5. Confirmer: Continuer vers Fadapay
6. Vérifier: Solde passe à 100,000 F ✓
```

### Scénario 2: Validation Montants
```
1. Cliquer: Recharger ⚡
2. Entrer: 500 F (trop faible)
3. Vérifier: Message d'erreur "Montant minimum est 1,000"
4. Entrer: 1,000,001 F (trop élevé)
5. Vérifier: Message d'erreur "Montant maximum est 1,000,000"
6. Entrer: 50,000 F (valide)
7. Vérifier: Pas d'erreur ✓
```

### Scénario 3: Déduction Automatique
```
1. Solde actuel: 100,000 F
2. Aller à: Partenaire Dashboard ou QR Scan
3. Scanner QR ou simuler transaction: 10,000 F
4. Attendre le traitement
5. Retourner à Portefeuille
6. Vérifier:
   - Solde: 109,875 F (100K + 10K - 125F de frais)
   - Revenus: augmentés de 125 F ✓
```

---

## 📚 Documentation Rapide

| Document | Quand l'utiliser |
|----------|------------------|
| **SUMMARY.md** | Aperçu général du projet |
| **DELIVERABLES.md** | Voir tous les livrables |
| **ARCHITECTURE.md** | Comprendre la structure technique |
| **WALLET_RECHARGE_README.md** | Docs techniques détaillées |
| **WALLET_RECHARGE_TESTING.md** | Guide complet de test |
| **CHECKLIST_IMPLEMENTATION.md** | Valider l'implémentation |
| **FILES_CREATED_AND_MODIFIED.md** | Voir tous les changements |
| **START.sh** | Script de démarrage |
| **QUICK_START.md** | Ce fichier! |

---

## 🆘 Dépannage Rapide

### Problème: Backend ne démarre pas

```bash
# Vérifier Python
python --version  # Doit être 3.8+

# Vérifier Django
cd c:\Hackathon\frontend1\backend
pip list | grep Django

# Réinstaller dépendances
pip install -r requirements.txt

# Réessayer
python manage.py runserver
```

### Problème: Frontend ne démarre pas

```bash
# Vérifier Node.js
node --version  # Doit être 18+
npm --version   # Doit être 8+

# Nettoyer cache
cd c:\Hackathon\frontend1\frontend1
rm -rf node_modules package-lock.json
npm install

# Réessayer
npm run dev
```

### Problème: Erreur de connexion

```
Vérifier les identifiants:
Email:    merchant@demo.local (exact)
Password: Demo123!@ (exact)

Vérifier:
- Base de données existe (backend/db.sqlite3)
- Utilisateur créé dans la base
```

### Problème: Modal ne s'ouvre pas

```
Vérifier:
1. Vous êtes connecté
2. Vous êtes sur la page "Portefeuille"
3. Bouton "Recharger ⚡" est visible
4. Console DevTools: F12 → Console tab → pas d'erreurs
```

### Problème: Erreur Fadapay

```
Vérifier:
1. Montant entre 1,000 et 1,000,000 F
2. Connexion Internet active
3. Backend logs pour erreurs (Terminal 1)
4. DevTools Network tab pour requêtes API
```

---

## 🎯 Objectifs de Test

### Frontend Functionality ✓
- [ ] Modal ouvre/ferme sans erreur
- [ ] Montants rapides fonctionnent (10K, 25K, 50K, 100K)
- [ ] Input personnalisé valide les montants
- [ ] Messages d'erreur affichés correctement
- [ ] Bouton "Continuer" appelle l'API
- [ ] États (loading, success, error) s'affichent
- [ ] Redirection Fadapay fonctionne

### Backend Functionality ✓
- [ ] GET /api/wallet/recharge/ retourne le solde
- [ ] POST /api/wallet/recharge/ accepte les requêtes
- [ ] Validation montants (1K-1M) fonctionne
- [ ] Appel Fadapay API réussit
- [ ] Response contient paymentUrl et rechargeId
- [ ] Erreurs gérées correctement
- [ ] Logs enregistrés

### Integration ✓
- [ ] WalletPage affiche le bouton "Recharger"
- [ ] Modal s'affiche au clic du bouton
- [ ] API appel exécuté avec Bearer token
- [ ] Solde mis à jour après recharge
- [ ] Historique enregistré
- [ ] Pas d'erreurs JavaScript/Python

### Auto Fee Deduction ✓
- [ ] Frais déduits automatiquement après QR scan
- [ ] 25% du frais_service prélevés
- [ ] Balance mise à jour correctement
- [ ] Revenus_generes augmentés
- [ ] Logs enregistrés
- [ ] CommissionRecord créé

---

## 📱 Appareils à Tester

```
✓ Desktop (Chrome, Firefox, Edge)
  - Résolution: 1920x1080
  - Vérifier: Modal et buttons

✓ Mobile (DevTools mobile)
  - iPhone 12 (390x844)
  - Android (360x800)
  - Vérifier: Design responsive

✓ Tablet (iPad Pro)
  - Résolution: 1024x1366
  - Vérifier: Layout adapté
```

---

## 🔗 URLs Principales

```
Frontend:
- Home:              http://localhost:5173
- Wallet:           http://localhost:5173 → Portefeuille
- Demo:             http://localhost:5173 → Démo

Backend:
- API Root:         http://localhost:8000/api/
- Wallet GET:       http://localhost:8000/api/wallet/recharge/
- Admin:            http://localhost:8000/admin/

Documentation:
- Docs locales:     c:\Hackathon\WALLET_RECHARGE_README.md
- Tests:            c:\Hackathon\WALLET_RECHARGE_TESTING.md
```

---

## 💡 Tips & Tricks

### Afficher les détails de l'API dans DevTools
```
1. Appuyer: F12 (ouvrir DevTools)
2. Aller à: Network tab
3. Refaire: Action (ex: Recharge)
4. Voir: Requête POST et réponse
5. Inspecter: Headers, Body, Response
```

### Voir les logs du Backend
```
Terminal 1 (Backend running):
- Regarder les messages
- POST /api/wallet/recharge/ [200 OK]
- Chercher erreurs ou warnings
```

### Tester les validations
```
Montants à essayer:
- 0 F → Error: "Montant doit être > 0"
- 500 F → Error: "Minimum est 1,000"
- 1,000 F → OK ✓
- 50,000 F → OK ✓
- 1,000,000 F → OK ✓
- 1,000,001 F → Error: "Maximum est 1,000,000"
- -10,000 F → Error: "Montant doit être positif"
```

### Voir les données en temps réel
```
Django Shell:
python manage.py shell
from api.models import Wallet, User
user = User.objects.get(email='merchant@demo.local')
wallet = user.wallet
print(f"Balance: {wallet.balance}")
print(f"En attente: {wallet.balance_en_attente}")
print(f"Revenus: {wallet.revenus_generes}")
```

---

## ✅ Votre Checklist Finale

### Avant de Commencer
- [ ] Python 3.8+ installé
- [ ] Node.js 18+ installé
- [ ] Git instalé (optionnel)
- [ ] Éditeur VS Code (optionnel mais recommandé)

### Environnement Setup
- [ ] Frontend1 folder ouvert dans VS Code
- [ ] Backend répertoire accessible
- [ ] Dépendances installées (pip, npm)
- [ ] Ports 8000 et 5173 disponibles

### Démarrage
- [ ] Backend terminal démarré
- [ ] Frontend terminal démarré
- [ ] Application accessible
- [ ] Connecté comme merchant

### Test de Base
- [ ] Page Portefeuille visible
- [ ] Bouton Recharger visible
- [ ] Modal s'ouvre
- [ ] Montants affichés
- [ ] Recharge réussit
- [ ] Solde mis à jour

### Tests Avancés
- [ ] Validation montants testée
- [ ] QR scan testé
- [ ] Frais déduits vérifiés
- [ ] Historique consulté
- [ ] Pas d'erreurs dans console
- [ ] Logs backend vérifiés

### Documentation
- [ ] Documentation lue
- [ ] Architecture comprise
- [ ] Tests exécutés
- [ ] Checklist complétée
- [ ] Prêt pour production

---

## 🎓 Prochaines Étapes

### Immédiat (Jour 1)
1. ✅ Exécuter Quick Start
2. ✅ Tester Recharge
3. ✅ Tester Déduction
4. ✅ Lire WALLET_RECHARGE_TESTING.md

### Court Terme (Semaine 1)
1. Configurer webhooks Fadapay
2. Tester avec vrai comptes test Fadapay
3. Configurer emails de confirmation
4. Ajouter notifications push

### Moyen Terme (Mois 1)
1. Déployer en staging
2. Tests E2E complets
3. Load testing
4. Déployer en production

### Optimisation Continuée
1. Monitoring et alertes
2. Rapports et analytics
3. Optimisation performance
4. Fonctionnalités additionnelles

---

## 📞 Support & Ressources

### Fichiers d'Aide
```
SUMMARY.md                    → Résumé général
DELIVERABLES.md               → Tous les livrables
ARCHITECTURE.md               → Architecture technique
WALLET_RECHARGE_README.md     → Documentation API
WALLET_RECHARGE_TESTING.md    → Guide de test
CHECKLIST_IMPLEMENTATION.md   → Validation
FILES_CREATED_AND_MODIFIED.md → Changements
```

### Codes de Test
```
merchant@demo.local
Password: Demo123!@
```

### Endpoints API
```
GET  /api/wallet/recharge/         → Get wallet status
POST /api/wallet/recharge/         → Initiate recharge
POST /api/qr/scan/                 → Scan QR (deduction)
GET  /api/wallet/                  → Get full wallet
```

---

## 🎉 Félicitations!

Vous avez maintenant:
✅ Système complet de recharge
✅ Déduction automatique des frais
✅ Interface utilisateur professionnelle
✅ Documentation complète
✅ Tests et validation

**Vous êtes prêt à monétiser vos transactions! 🚀**

---

**Bon démarrage! 💪**

*Questions? Consultez les fichiers de documentation.*
