import React, { useState } from 'react';
import { AlertCircle, CheckCircle, Zap, DollarSign, ArrowRight, TrendingDown } from 'lucide-react';

interface TransactionStep {
  id: number;
  title: string;
  description: string;
  details: string[];
  icon: React.ReactNode;
}

export const WalletRechargeDemo: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);

  const steps: TransactionStep[] = [
    {
      id: 1,
      title: "Commerçant clique sur 'Recharger'",
      description: "Le modal de recharge s'ouvre avec les montants rapides",
      details: [
        "Solde actuel affiché: 50,000 F",
        "Options rapides: 10K, 25K, 50K, 100K F",
        "Min: 1,000 F | Max: 1,000,000 F",
      ],
      icon: <Zap size={24} />,
    },
    {
      id: 2,
      title: "Sélection du montant",
      description: "Le commerçant choisit le montant à recharger (ex: 50,000 F)",
      details: [
        "Montant sélectionné: 50,000 F",
        "Validation du montant (min/max)",
        "Bouton 'Continuer vers Fadapay' activé",
      ],
      icon: <DollarSign size={24} />,
    },
    {
      id: 3,
      title: "Requête API vers Fadapay",
      description: "POST /api/wallet/recharge/ envoyé au backend",
      details: [
        "Payload: { amount: 50000, currency: 'XOF' }",
        "Headers: Authorization Bearer token",
        "Backend crée un ID de recharge unique",
      ],
      icon: <ArrowRight size={24} />,
    },
    {
      id: 4,
      title: "Redirection Fadapay",
      description: "L'URL de paiement Fadapay est retournée et ouvre",
      details: [
        "Frontend reçoit: paymentUrl, rechargeId, reference",
        "Redirection automatique vers le formulaire de paiement Fadapay",
        "Commerçant effectue le paiement (carte, mobile money, etc.)",
      ],
      icon: <CheckCircle size={24} style={{ color: '#22c55e' }} />,
    },
    {
      id: 5,
      title: "Paiement reçu ✓",
      description: "Le portefeuille est crédité du montant",
      details: [
        "Solde avant: 50,000 F",
        "+ Recharge: 50,000 F",
        "= Nouveau solde: 100,000 F",
      ],
      icon: <CheckCircle size={24} style={{ color: '#10b981' }} />,
    },
    {
      id: 6,
      title: "Client scanne le QR code",
      description: "Le client scanne un code QR pour obtenir la monnaie",
      details: [
        "Transaction validée: 10,000 F à distribuer",
        "Frais service: 500 F (5% commission)",
        "POST /api/qr/scan/ déclenche le règlement",
      ],
      icon: <AlertCircle size={24} style={{ color: '#f59e0b' }} />,
    },
    {
      id: 7,
      title: "Distribuer la monnaie (dans l'app)",
      description: "Le commerçant donne 10,000 F au client",
      details: [
        "Solde avant distribution: 100,000 F",
        "Montant distribué: 10,000 F",
        "Solde intermédiaire: 110,000 F",
      ],
      icon: <DollarSign size={24} style={{ color: '#3b82f6' }} />,
    },
    {
      id: 8,
      title: "Prélèvement automatique des frais",
      description: "Les frais sont déduits APRÈS la distribution",
      details: [
        "Solde avant prélèvement: 110,000 F",
        "- Frais service (25%): 500 F",
        "= Solde final: 109,500 F",
      ],
      icon: <TrendingDown size={24} style={{ color: '#ef4444' }} />,
    },
  ];

  const currentStep = steps[activeStep];
  const progress = ((activeStep + 1) / steps.length) * 100;

  return (
    <div style={{
      maxWidth: '1000px',
      margin: '0 auto',
      padding: '40px 20px',
      fontFamily: 'system-ui, -apple-system, sans-serif',
    }}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .step-content {
          animation: fadeIn 0.4s ease;
        }
      `}</style>

      {/* Header */}
      <div style={{ marginBottom: '40px' }}>
        <h1 style={{
          fontSize: '28px',
          fontWeight: 700,
          marginBottom: '8px',
          color: '#1f2937',
        }}>
          Démo: Système de Recharge Portefeuille
        </h1>
        <p style={{
          fontSize: '15px',
          color: '#6b7280',
          lineHeight: 1.6,
        }}>
          Parcourez le flux complet de recharge et de déduction automatique des frais
        </p>
      </div>

      {/* Progress Bar */}
      <div style={{
        marginBottom: '40px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}>
        <div style={{
          fontSize: '13px',
          fontWeight: 600,
          color: '#6b7280',
          display: 'flex',
          justifyContent: 'space-between',
        }}>
          <span>Étape {activeStep + 1} sur {steps.length}</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div style={{
          width: '100%',
          height: '8px',
          background: '#e5e7eb',
          borderRadius: '100px',
          overflow: 'hidden',
        }}>
          <div style={{
            height: '100%',
            background: 'linear-gradient(90deg, #3b82f6, #10b981)',
            width: `${progress}%`,
            transition: 'width 0.4s ease',
          }} />
        </div>
      </div>

      {/* Main Content */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '40px',
        marginBottom: '40px',
        alignItems: 'start',
      }}>
        {/* Left: Step Details */}
        <div className="step-content" style={{
          background: '#f9fafb',
          border: '1px solid #e5e7eb',
          borderRadius: '12px',
          padding: '32px',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            marginBottom: '24px',
          }}>
            <div style={{
              width: '52px',
              height: '52px',
              borderRadius: '50%',
              background: 'white',
              border: '2px solid #3b82f6',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#3b82f6',
            }}>
              {currentStep.icon}
            </div>
            <div>
              <h2 style={{
                fontSize: '20px',
                fontWeight: 700,
                margin: '0 0 4px 0',
                color: '#1f2937',
              }}>
                {currentStep.title}
              </h2>
              <p style={{
                margin: 0,
                fontSize: '14px',
                color: '#6b7280',
              }}>
                {currentStep.description}
              </p>
            </div>
          </div>

          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}>
            {currentStep.details.map((detail, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                fontSize: '14px',
                color: '#374151',
              }}>
                <span style={{
                  minWidth: '20px',
                  height: '20px',
                  background: '#dbeafe',
                  color: '#3b82f6',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                  fontWeight: 700,
                  marginTop: '2px',
                  flexShrink: 0,
                }}>
                  {i + 1}
                </span>
                <span>{detail}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Visual Representation */}
        <div className="step-content" style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}>
          {/* Wallet State */}
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: '12px',
            padding: '24px',
          }}>
            <div style={{ fontSize: '13px', opacity: 0.8, marginBottom: '8px' }}>
              Solde du portefeuille
            </div>
            <div style={{
              fontSize: '32px',
              fontWeight: 700,
              fontFamily: 'monospace',
            }}>
              {activeStep < 4 ? '50,000' : activeStep < 6 ? '100,000' : activeStep < 8 ? '110,000' : '109,500'} F
            </div>
            <div style={{
              fontSize: '12px',
              opacity: 0.8,
              marginTop: '12px',
              paddingTop: '12px',
              borderTop: '1px solid rgba(255,255,255,0.2)',
            }}>
              {activeStep < 2 && 'En attente de recharge...'}
              {activeStep === 2 && 'Traitement de la recharge...'}
              {activeStep === 3 && 'Redirection vers Fadapay...'}
              {activeStep === 4 && 'Recharge confirmée ✓'}
              {activeStep === 5 && 'QR code en attente...'}
              {activeStep === 6 && 'Monnaie distribuée'}
              {activeStep === 7 && 'Frais prélevés automatiquement ✓'}
            </div>
          </div>

          {/* Transaction Timeline */}
          <div style={{
            background: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
            padding: '20px',
          }}>
            <div style={{
              fontSize: '13px',
              fontWeight: 600,
              marginBottom: '16px',
              color: '#1f2937',
            }}>
              Historique des opérations
            </div>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}>
              {[
                { action: 'Recharge initiée', amount: '+50,000 F', active: activeStep >= 4 },
                { action: 'Recharge confirmée', amount: '+50,000 F', active: activeStep >= 4 },
                { action: 'Monnaie distribuée', amount: '+10,000 F', active: activeStep >= 6 },
                { action: 'Frais prélevés', amount: '-500 F', active: activeStep >= 7 },
              ].map((item, i) => (
                <div key={i} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px',
                  background: item.active ? '#f0fdf4' : '#f3f4f6',
                  borderRadius: '8px',
                  opacity: item.active ? 1 : 0.5,
                  transition: 'all 0.3s ease',
                }}>
                  <span style={{
                    fontSize: '14px',
                    fontWeight: 500,
                    color: '#374151',
                  }}>
                    {item.action}
                  </span>
                  <span style={{
                    fontSize: '14px',
                    fontWeight: 700,
                    color: item.amount.startsWith('+') ? '#10b981' : '#ef4444',
                    fontFamily: 'monospace',
                  }}>
                    {item.amount}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div style={{
        display: 'flex',
        gap: '12px',
        justifyContent: 'center',
        flexWrap: 'wrap',
      }}>
        <button
          onClick={() => setActiveStep(Math.max(0, activeStep - 1))}
          disabled={activeStep === 0}
          style={{
            padding: '10px 20px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            background: 'white',
            cursor: activeStep === 0 ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: 600,
            color: '#1f2937',
            opacity: activeStep === 0 ? 0.5 : 1,
            transition: 'all 0.2s',
          }}
        >
          ← Précédent
        </button>

        {steps.map((_, i) => (
          <button
            key={i}
            onClick={() => setActiveStep(i)}
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '8px',
              border: i === activeStep ? '2px solid #3b82f6' : '1px solid #d1d5db',
              background: i === activeStep ? '#3b82f6' : i < activeStep ? '#10b981' : 'white',
              color: i === activeStep || i < activeStep ? 'white' : '#6b7280',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 600,
              transition: 'all 0.2s',
            }}
          >
            {i < activeStep ? '✓' : i + 1}
          </button>
        ))}

        <button
          onClick={() => setActiveStep(Math.min(steps.length - 1, activeStep + 1))}
          disabled={activeStep === steps.length - 1}
          style={{
            padding: '10px 20px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            background: 'white',
            cursor: activeStep === steps.length - 1 ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: 600,
            color: '#1f2937',
            opacity: activeStep === steps.length - 1 ? 0.5 : 1,
            transition: 'all 0.2s',
          }}
        >
          Suivant →
        </button>
      </div>

      {/* Info Box */}
      <div style={{
        marginTop: '40px',
        padding: '20px',
        background: '#eff6ff',
        border: '1px solid #bfdbfe',
        borderRadius: '8px',
        color: '#1e40af',
        fontSize: '14px',
        lineHeight: 1.6,
      }}>
        <strong>ℹ️ Résumé:</strong> Le commerçant peut recharger son portefeuille via Fadapay. 
        Après chaque transaction QR, les frais sont automatiquement prélevés du solde. 
        Flux: Recharge Fadapay → Distribution monnaie (+) → Déduction frais (-) → Solde final
      </div>
    </div>
  );
};

export default WalletRechargeDemo;
