import React, { useState } from 'react';
import { X, Loader, AlertCircle, CheckCircle, Zap } from 'lucide-react';
import { rechargeWallet } from '../api';

interface WalletRechargeModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentBalance: number | string;
  userRole: string;
}

export const WalletRechargeModal: React.FC<WalletRechargeModalProps> = ({
  isOpen,
  onClose,
  currentBalance,
  userRole,
}) => {
  const [amount, setAmount] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState(false);
  const [paymentUrl, setPaymentUrl] = useState<string>('');
  const [rechargeId, setRechargeId] = useState<string>('');

  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    setAmount(value);
    setError('');
  };

  const handleQuickAmount = (value: number) => {
    setAmount(value.toString());
    setError('');
  };

  const handleSubmit = async () => {
    setError('');

    if (!amount) {
      setError('Veuillez entrer un montant');
      return;
    }

    const numAmount = parseInt(amount, 10);
    if (numAmount < 1000) {
      setError('Le montant minimum est 1,000 XOF');
      return;
    }

    if (numAmount > 1000000) {
      setError('Le montant maximum est 1,000,000 XOF');
      return;
    }

    setLoading(true);
    try {
      const result = await rechargeWallet(numAmount, 'XOF');
      
      if (result.success && result.paymentUrl) {
        setRechargeId(result.rechargeId || '');
        setPaymentUrl(result.paymentUrl);
        setSuccess(true);

        // Rediriger vers Fadapay après 2 secondes
        setTimeout(() => {
          if (result.paymentUrl) {
            window.location.href = result.paymentUrl;
          }
        }, 2000);
      } else {
        setError('Erreur lors de l\'initiation de la recharge');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la recharge');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setAmount('');
    setError('');
    setSuccess(false);
    setPaymentUrl('');
    setRechargeId('');
  };

  const handleClose = () => {
    handleReset();
    onClose();
  };

  if (!isOpen) return null;

  const currentBalanceNum = typeof currentBalance === 'string' 
    ? parseFloat(currentBalance) 
    : currentBalance;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px',
    }}>
      <div style={{
        background: 'var(--bg)',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '420px',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          padding: '24px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <h2 style={{
            margin: 0,
            fontSize: '18px',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: 'var(--text)',
          }}>
            <Zap size={20} style={{ color: 'var(--info)' }} />
            Recharger votre portefeuille
          </h2>
          <button
            onClick={handleClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-muted)',
              padding: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            disabled={loading}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Current Balance */}
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border)',
            borderRadius: '12px',
            padding: '16px',
            textAlign: 'center',
          }}>
            <div style={{
              fontSize: '12px',
              color: 'var(--text-muted)',
              marginBottom: '4px',
            }}>
              Solde actuel
            </div>
            <div style={{
              fontSize: '28px',
              fontWeight: 700,
              color: 'var(--info)',
              fontFamily: 'var(--font-display)',
            }}>
              {currentBalanceNum.toLocaleString('fr')} F
            </div>
          </div>

          {success ? (
            // Success State
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '16px',
              padding: '24px 0',
            }}>
              <div style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'var(--success-dim)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--success)',
              }}>
                <CheckCircle size={40} />
              </div>
              <div style={{ textAlign: 'center' }}>
                <h3 style={{
                  margin: '0 0 8px 0',
                  fontSize: '18px',
                  fontWeight: 700,
                  color: 'var(--text)',
                }}>
                  Recharge initiée
                </h3>
                <p style={{
                  margin: 0,
                  fontSize: '14px',
                  color: 'var(--text-muted)',
                  lineHeight: 1.5,
                }}>
                  Vous allez être redirigé vers Fadapay pour finaliser le paiement.
                </p>
              </div>
              <div style={{
                width: '100%',
                background: 'var(--bg-surface)',
                borderRadius: '8px',
                padding: '12px',
                fontSize: '13px',
                color: 'var(--text-muted)',
                textAlign: 'center',
                fontFamily: 'monospace',
                wordBreak: 'break-all',
              }}>
                ID: {rechargeId}
              </div>
            </div>
          ) : (
            // Input State
            <>
              {/* Amount Input */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: 600,
                  marginBottom: '8px',
                  color: 'var(--text)',
                }}>
                  Montant à recharger (XOF)
                </label>
                <input
                  type="text"
                  value={amount}
                  onChange={handleAmountChange}
                  placeholder="Entrez le montant"
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: `1px solid ${error ? 'var(--danger)' : 'var(--border)'}`,
                    borderRadius: '8px',
                    fontSize: '16px',
                    background: 'var(--bg-surface)',
                    color: 'var(--text)',
                    boxSizing: 'border-box',
                    transition: 'border-color 0.3s',
                    fontFamily: 'monospace',
                  }}
                />
                {error && (
                  <div style={{
                    fontSize: '12px',
                    color: 'var(--danger)',
                    marginTop: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}>
                    <AlertCircle size={14} />
                    {error}
                  </div>
                )}
              </div>

              {/* Quick Amounts */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '10px',
              }}>
                {[10000, 25000, 50000, 100000].map((value) => (
                  <button
                    key={value}
                    onClick={() => handleQuickAmount(value)}
                    disabled={loading}
                    style={{
                      padding: '12px',
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      background: amount === value.toString() ? 'var(--info)' : 'var(--bg-surface)',
                      color: amount === value.toString() ? 'white' : 'var(--text)',
                      fontWeight: 600,
                      fontSize: '14px',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      transition: 'all 0.3s',
                      opacity: loading ? 0.5 : 1,
                    }}
                  >
                    {value.toLocaleString('fr')} F
                  </button>
                ))}
              </div>

              {/* Info */}
              <div style={{
                background: 'var(--info-dim)',
                border: '1px solid var(--info)',
                borderRadius: '8px',
                padding: '12px',
                fontSize: '12px',
                color: 'var(--info)',
                lineHeight: 1.5,
              }}>
                ℹ️ Min: 1,000 F | Max: 1,000,000 F
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        {!success && (
          <div style={{
            padding: '20px 24px',
            borderTop: '1px solid var(--border)',
            display: 'flex',
            gap: '12px',
          }}>
            <button
              onClick={handleClose}
              disabled={loading}
              style={{
                flex: 1,
                padding: '12px',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                background: 'transparent',
                color: 'var(--text)',
                fontWeight: 600,
                fontSize: '14px',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.5 : 1,
                transition: 'all 0.3s',
              }}
            >
              Annuler
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading || !amount}
              style={{
                flex: 1,
                padding: '12px',
                border: 'none',
                borderRadius: '8px',
                background: !amount || loading ? 'var(--text-muted)' : 'var(--info)',
                color: 'white',
                fontWeight: 600,
                fontSize: '14px',
                cursor: loading || !amount ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                opacity: loading || !amount ? 0.5 : 1,
                transition: 'all 0.3s',
              }}
            >
              {loading ? (
                <>
                  <Loader size={16} style={{ animation: 'spin 1s linear infinite' }} />
                  Traitement...
                </>
              ) : (
                'Continuer vers Fadapay'
              )}
            </button>
          </div>
        )}

        {success && (
          <div style={{
            padding: '20px 24px',
            borderTop: '1px solid var(--border)',
            display: 'flex',
            gap: '12px',
          }}>
            <button
              onClick={handleClose}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                background: 'transparent',
                color: 'var(--text)',
                fontWeight: 600,
                fontSize: '14px',
                cursor: 'pointer',
                transition: 'all 0.3s',
              }}
            >
              Fermer
            </button>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
