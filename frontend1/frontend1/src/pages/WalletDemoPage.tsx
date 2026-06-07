import React, { useState } from 'react';
import { WalletRechargeDemo } from '../components/WalletRechargeDemo';
import { WalletRechargeModal } from '../components/WalletRechargeModal';
import { TestSection } from '../components/TestSection';
import { BookOpen, Zap, Play } from 'lucide-react';

const WalletDemoPage: React.FC = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [mockBalance] = useState(45000);

  return (
    <div style={{
      padding: '20px',
      maxWidth: '1200px',
      margin: '0 auto',
      animation: 'fadeUp 0.4s ease',
    }}>
      {/* Page Header */}
      <div style={{ marginBottom: '40px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <Zap size={28} style={{ color: '#3b82f6' }} />
          <h1 className="page-title">Démo: Recharge Portefeuille</h1>
        </div>
        <p className="page-subtitle">
          Testez le système de recharge via Fadapay et la déduction automatique des frais
        </p>
      </div>

      {/* Quick Test Section */}
      <div className="card" style={{
        marginBottom: '40px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '32px',
        borderRadius: '12px',
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px', alignItems: 'center' }}>
          <div>
            <h2 style={{
              fontSize: '24px',
              fontWeight: 700,
              marginBottom: '12px',
              margin: 0,
            }}>
              Testez le modal de recharge
            </h2>
            <p style={{
              fontSize: '15px',
              opacity: 0.9,
              lineHeight: 1.6,
              margin: '12px 0 0 0',
            }}>
              Cliquez sur le bouton ci-dessous pour voir le modal de recharge en action. 
              Sélectionnez un montant et testez l'intégration Fadapay.
            </p>
            <button
              onClick={() => setModalOpen(true)}
              style={{
                marginTop: '20px',
                padding: '12px 28px',
                background: 'white',
                color: '#667eea',
                border: 'none',
                borderRadius: '8px',
                fontSize: '15px',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'all 0.3s',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-2px)';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 8px 20px rgba(0,0,0,0.15)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(0)';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = 'none';
              }}
            >
              <Play size={16} /> Ouvrir Modal de Recharge
            </button>
          </div>
          <div style={{
            background: 'rgba(255,255,255,0.1)',
            borderRadius: '8px',
            padding: '24px',
            textAlign: 'center',
          }}>
            <div style={{
              fontSize: '14px',
              opacity: 0.9,
              marginBottom: '8px',
            }}>
              Solde actuel (simulation)
            </div>
            <div style={{
              fontSize: '36px',
              fontWeight: 700,
              fontFamily: 'monospace',
            }}>
              {mockBalance.toLocaleString('fr')} F
            </div>
          </div>
        </div>
      </div>

      {/* Features Overview */}
      <div style={{
        marginBottom: '40px',
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '20px',
      }}>
        {[
          {
            title: 'Recharge Fadapay',
            description: 'Chargez votre portefeuille en quelques clics via le passerelle Fadapay sécurisée.',
            icon: '💳',
          },
          {
            title: 'Déduction Auto',
            description: 'Les frais sont automatiquement prélevés du solde après chaque transaction QR.',
            icon: '🔄',
          },
          {
            title: 'Historique',
            description: 'Consultez l\'historique complet de vos recharges et transactions.',
            icon: '📊',
          },
        ].map((feature, i) => (
          <div key={i} className="card" style={{
            padding: '24px',
            textAlign: 'center',
          }}>
            <div style={{
              fontSize: '32px',
              marginBottom: '12px',
            }}>
              {feature.icon}
            </div>
            <h3 style={{
              fontSize: '16px',
              fontWeight: 700,
              marginBottom: '8px',
              margin: '0 0 8px 0',
            }}>
              {feature.title}
            </h3>
            <p style={{
              fontSize: '14px',
              color: 'var(--text-muted)',
              lineHeight: 1.6,
              margin: 0,
            }}>
              {feature.description}
            </p>
          </div>
        ))}
      </div>

      {/* Interactive Demo */}
      <div style={{ marginBottom: '40px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '20px',
        }}>
          <BookOpen size={20} style={{ color: '#3b82f6' }} />
          <h2 style={{
            fontSize: '20px',
            fontWeight: 700,
            margin: 0,
          }}>
            Parcours Complet: Recharge → Distribution → Déduction
          </h2>
        </div>
        <WalletRechargeDemo />
      </div>

      {/* API Documentation */}
      <div className="card" style={{ marginBottom: '40px' }}>
        <h3 style={{
          fontSize: '18px',
          fontWeight: 700,
          marginBottom: '16px',
          margin: '0 0 16px 0',
        }}>
          Documentation API
        </h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '24px',
        }}>
          {/* POST /api/wallet/recharge/ */}
          <div style={{
            background: 'var(--bg-surface)',
            borderRadius: '8px',
            padding: '16px',
            border: '1px solid var(--border)',
          }}>
            <div style={{
              fontSize: '13px',
              fontWeight: 700,
              color: 'var(--info)',
              marginBottom: '8px',
              fontFamily: 'monospace',
            }}>
              POST /api/wallet/recharge/
            </div>
            <div style={{
              fontSize: '13px',
              color: 'var(--text-muted)',
              marginBottom: '12px',
              lineHeight: 1.6,
            }}>
              Initie une recharge de portefeuille via Fadapay
            </div>
            <div style={{
              background: 'var(--bg)',
              padding: '12px',
              borderRadius: '6px',
              fontSize: '11px',
              fontFamily: 'monospace',
              overflow: 'auto',
              color: 'var(--text-muted)',
              marginBottom: '12px',
            }}>
              {`{
  "amount": 50000,
  "currency": "XOF"
}`}
            </div>
            <div style={{
              fontSize: '12px',
              color: 'var(--success)',
            }}>
              ✓ Retourne: paymentUrl, rechargeId, reference
            </div>
          </div>

          {/* GET /api/wallet/recharge/ */}
          <div style={{
            background: 'var(--bg-surface)',
            borderRadius: '8px',
            padding: '16px',
            border: '1px solid var(--border)',
          }}>
            <div style={{
              fontSize: '13px',
              fontWeight: 700,
              color: 'var(--success)',
              marginBottom: '8px',
              fontFamily: 'monospace',
            }}>
              GET /api/wallet/recharge/
            </div>
            <div style={{
              fontSize: '13px',
              color: 'var(--text-muted)',
              marginBottom: '12px',
              lineHeight: 1.6,
            }}>
              Récupère l'état du portefeuille
            </div>
            <div style={{
              background: 'var(--bg)',
              padding: '12px',
              borderRadius: '6px',
              fontSize: '11px',
              fontFamily: 'monospace',
              overflow: 'auto',
              color: 'var(--text-muted)',
              marginBottom: '12px',
            }}>
              {`{
  "balance": "100000",
  "balance_en_attente": "5000",
  "revenus_generes": "25000"
}`}
            </div>
            <div style={{
              fontSize: '12px',
              color: 'var(--success)',
            }}>
              ✓ Affiche tous les soldes
            </div>
          </div>
        </div>
      </div>

      {/* Flow Diagram */}
      <div className="card" style={{
        background: 'var(--bg-surface)',
        padding: '24px',
        borderRadius: '12px',
      }}>
        <h3 style={{
          fontSize: '18px',
          fontWeight: 700,
          marginBottom: '20px',
          margin: '0 0 20px 0',
        }}>
          Flux de Traitement Complet
        </h3>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
        }}>
          {[
            { label: 'Recharge', icon: '1️⃣' },
            { label: 'Fadapay', icon: '2️⃣' },
            { label: 'Crédit', icon: '3️⃣' },
            { label: 'QR Scan', icon: '4️⃣' },
            { label: 'Distribution', icon: '5️⃣' },
            { label: 'Déduction', icon: '6️⃣' },
            { label: 'Final', icon: '7️⃣' },
          ].map((step, i) => (
            <React.Fragment key={i}>
              <div style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                padding: '12px 20px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: 700,
                textAlign: 'center',
                minWidth: '120px',
              }}>
                <div style={{ fontSize: '18px', marginBottom: '4px' }}>{step.icon}</div>
                {step.label}
              </div>
              {i < 6 && (
                <div style={{
                  color: 'var(--text-muted)',
                  fontSize: '20px',
                  fontWeight: 700,
                }}>
                  →
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Modal Component */}
      <WalletRechargeModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        currentBalance={mockBalance}
        userRole="merchant"
      />
    </div>
  );
};

export default WalletDemoPage;
