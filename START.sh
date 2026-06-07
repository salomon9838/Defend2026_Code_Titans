#!/bin/bash
# Script de démarrage rapide du système

echo "🚀 SmartChange - Wallet Recharge System"
echo "========================================"
echo ""
echo "Cet script démarre:"
echo "  1. Backend Django (http://localhost:8000)"
echo "  2. Frontend React (http://localhost:5173)"
echo ""

# Configuration
BACKEND_DIR="c:\\Hackathon\\frontend1\\backend"
FRONTEND_DIR="c:\\Hackathon\\frontend1\\frontend1"

# Vérifier les répertoires
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Backend directory not found: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

echo "✅ Directories found"
echo ""

# Instructions
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    DÉMARRAGE MANUEL                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "TERMINAL 1 - Backend Django:"
echo "  cd $BACKEND_DIR"
echo "  python manage.py runserver"
echo ""
echo "TERMINAL 2 - Frontend React:"
echo "  cd $FRONTEND_DIR"
echo "  npm run dev"
echo ""
echo "ACCÈS:"
echo "  • API: http://localhost:8000/api/"
echo "  • Frontend: http://localhost:5173"
echo ""
echo "CONNEXION:"
echo "  Email: merchant@demo.local"
echo "  Password: Demo123!@"
echo ""
echo "TEST RAPIDE:"
echo "  1. Ouvrir http://localhost:5173"
echo "  2. Se connecter"
echo "  3. Aller à 'Portefeuille'"
echo "  4. Cliquer 'Recharger ⚡'"
echo "  5. Sélectionner 50,000 F"
echo "  6. Vérifier que le solde passe à 100,000 F ✓"
echo ""
echo "DOCUMENTATION:"
echo "  • SUMMARY.md - Résumé rapide"
echo "  • WALLET_RECHARGE_README.md - Documentation technique"
echo "  • WALLET_RECHARGE_TESTING.md - Scénarios de test"
echo "  • IMPLEMENTATION_COMPLETE.md - Guide complet"
echo ""
echo "✨ Système prêt pour démarrage! 🚀"
