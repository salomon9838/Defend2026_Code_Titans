import React, { useEffect, useState } from 'react';
import { MapPin, Navigation, Clock, Phone, Star, Search, User } from 'lucide-react';
import type { PartnerLocation, PartnerShop, User as UserType } from '../types';
import { getPartnerLocations, getPartners, requestPartnerService, getCustomers } from '../api';

const GeolocationPage: React.FC = () => {
  const [selected, setSelected] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [showMap, setShowMap] = useState(true);
  const [partners, setPartners] = useState<PartnerShop[]>([]);
  const [partnerLocations, setPartnerLocations] = useState<PartnerLocation[]>([]);
  const [selectedLocationId, setSelectedLocationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [locationsLoading, setLocationsLoading] = useState(false);
  const [requesting, setRequesting] = useState(false);
  const [requestMessage, setRequestMessage] = useState<string | null>(null);
  // Customer selection
  const [customers, setCustomers] = useState<UserType[]>([]);
  const [customerSearch, setCustomerSearch] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState<UserType | null>(null);
  const [searchingCustomers, setSearchingCustomers] = useState(false);
  // Client identifier fields
  const [clientMontant, setClientMontant] = useState('');

  useEffect(() => {
    const loadCustomers = async () => {
      if (!customerSearch) {
        setCustomers([]);
        return;
      }
      setSearchingCustomers(true);
      try {
        const data = await getCustomers(customerSearch);
        setCustomers(data);
      } catch (e) {
        console.error('Erreur chargement clients', e);
      } finally {
        setSearchingCustomers(false);
      }
    };

    const timer = setTimeout(() => loadCustomers(), 300);
    return () => clearTimeout(timer);
  }, [customerSearch]);

  useEffect(() => {
    const loadPartners = async () => {
      setLoading(true);
      try {
        const data = await getPartners();
        setPartners(data);
      } catch (error) {
        console.error('Impossible de charger les partenaires', error);
      } finally {
        setLoading(false);
      }
    };
    loadPartners();
  }, []);

  const filtered = partners.filter(p =>
    p.nomBoutique?.toLowerCase().includes(search.toLowerCase()) ||
    p.adresse?.toLowerCase().includes(search.toLowerCase())
  );
  const selectedPartner = partners.find(p => p.id === selected);

  useEffect(() => {
    if (!selectedPartner) {
      setPartnerLocations([]);
      setSelectedLocationId(null);
      return;
    }

    const loadLocations = async () => {
      setLocationsLoading(true);
      try {
        const locations = await getPartnerLocations(String(selectedPartner.id));
        setPartnerLocations(locations);
        setSelectedLocationId(locations.length ? String(locations[0].id) : null);
      } catch (error) {
        console.error('Impossible de charger les emplacements du partenaire', error);
        setPartnerLocations([]);
        setSelectedLocationId(null);
      } finally {
        setLocationsLoading(false);
      }
    };

    loadLocations();
  }, [selectedPartner]);

  const handleRequestService = async () => {
    if (!selectedPartner) return;
    setRequesting(true);
    setRequestMessage(null);

    try {
      await requestPartnerService({
        partnerId: String(selectedPartner.id),
        partnerLocationId: selectedLocationId ? Number(selectedLocationId) : undefined,
        montantService: clientMontant ? parseFloat(clientMontant) : 25,
        commission: 25,
        clientIdentifier: selectedCustomer ? `${selectedCustomer.prenom} ${selectedCustomer.nom}` : 'Client anonyme',
        customerId: selectedCustomer?.id ? Number(selectedCustomer.id) : undefined,
      });
      setRequestMessage('Demande envoyée au partenaire.');
      // Reset fields
      setSelectedCustomer(null);
      setCustomerSearch('');
      setClientMontant('');
    } catch (error: any) {
      setRequestMessage(error.message || 'Erreur lors de l\'envoi de la demande.');
    } finally {
      setRequesting(false);
    }
  };

  return (
    <div style={{ animation: 'fadeUp 0.4s ease' }}>
      <div style={{ marginBottom: 16 }}>
        <h1 className="page-title">Partenaires proches</h1>
        <p className="page-subtitle">Récupérez votre monnaie chez un partenaire</p>
      </div>

      <div style={{ position: 'relative', marginBottom: 14 }}>
        <Search size={14} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
        <input
          className="input"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Rechercher un partenaire..."
          style={{ paddingLeft: 42 }}
        />
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
        <button
          onClick={() => setShowMap(true)}
          className="btn btn-sm"
          style={{
            flex: 1,
            justifyContent: 'center',
            background: showMap ? 'var(--primary-dim)' : 'var(--bg-surface)',
            border: `1px solid ${showMap ? 'var(--primary)' : 'var(--border)'}`,
            color: showMap ? 'var(--primary)' : 'var(--text-muted)',
          }}
        >
          🗺️ Carte
        </button>
        <button
          onClick={() => setShowMap(false)}
          className="btn btn-sm"
          style={{
            flex: 1,
            justifyContent: 'center',
            background: !showMap ? 'var(--primary-dim)' : 'var(--bg-surface)',
            border: `1px solid ${!showMap ? 'var(--primary)' : 'var(--border)'}`,
            color: !showMap ? 'var(--primary)' : 'var(--text-muted)',
          }}
        >
          📋 Liste
        </button>
      </div>

      <div style={{ display: 'flex', gap: 14, height: 'calc(100vh - 280px)', minHeight: 420 }}>
        <div
          style={{
            width: 300,
            flexShrink: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
            overflowY: 'auto',
          }}
          className={`geo-list-panel${!showMap ? ' hide' : ''}`}
        >
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', flexShrink: 0 }}>
            {loading ? 'Chargement...' : `${filtered.length} partenaire${filtered.length > 1 ? 's' : ''}`}
          </div>
          {filtered.map(partner => (
            <div
              key={partner.id}
              onClick={() => setSelected(partner.id === selected ? null : partner.id)}
              style={{
                background: selected === partner.id ? 'var(--primary-dim)' : 'var(--bg-card)',
                border: `1px solid ${selected === partner.id ? 'var(--primary)' : 'var(--border)'}`,
                borderRadius: 'var(--radius)',
                padding: '12px 14px',
                cursor: 'pointer',
                transition: 'all 0.15s',
                flexShrink: 0,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{partner.nomBoutique}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 3, marginTop: 2 }}>
                    <MapPin size={9} />{partner.adresse}
                  </div>
                </div>
                <div style={{ background: 'var(--success-dim)', color: 'var(--success)', padding: '2px 7px', borderRadius: 6, fontSize: 11, fontWeight: 700, flexShrink: 0 }}>
                  {partner.distance ?? 0} km
                </div>
              </div>
              <div style={{ display: 'flex', gap: 10, fontSize: 11 }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 3, color: 'var(--text-muted)' }}><Clock size={10} />{partner.horaires}</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 3, color: 'var(--warning)' }}><Star size={10} fill="currentColor" />4.8</span>
              </div>
              {selected === partner.id && (
                <div style={{ marginTop: 10, display: 'flex', gap: 7, flexWrap: 'wrap' }}>
                  <a
                    href={`https://maps.google.com/?q=${partner.latitude},${partner.longitude}`}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-primary btn-sm"
                    style={{ flex: 1, justifyContent: 'center', textDecoration: 'none' }}
                    onClick={e => e.stopPropagation()}
                  >
                    <Navigation size={12} /> Itinéraire
                  </a>
                  <button className="btn btn-secondary btn-sm" style={{ flex: 1 }} onClick={e => e.stopPropagation()}>
                    <Phone size={12} /> Appeler
                  </button>
                  <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
                    {locationsLoading ? (
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Chargement des emplacements...</div>
                    ) : partnerLocations.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        <label htmlFor="partner-location" style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)' }}>
                          Lieu de retrait
                        </label>
                        <select
                          id="partner-location"
                          className="input"
                          value={selectedLocationId ?? ''}
                          onChange={e => setSelectedLocationId(e.target.value)}
                          onClick={e => e.stopPropagation()}
                          onKeyDown={e => e.stopPropagation()}
                          style={{ width: '100%' }}
                        >
                          {partnerLocations.map(location => (
                            <option key={location.id} value={location.id}>
                              {location.nom} — {location.adresse}
                            </option>
                          ))}
                        </select>
                      </div>
                    ) : (
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Aucun emplacement de partenaire détecté, la demande sera envoyée sans lieu spécifique.</div>
                    )}

                    {/* Client selection */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 700, color: 'var(--text-muted)' }}>
                        <User size={14} />
                        Sélectionner le client
                      </div>
                      {selectedCustomer ? (
                        <div style={{
                          background: 'var(--bg-surface)',
                          borderRadius: 'var(--radius-sm)',
                          padding: 10,
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          border: '1px solid var(--border-bright)'
                        }}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <span style={{ fontWeight: 700, fontSize: 13 }}>{selectedCustomer.prenom} {selectedCustomer.nom}</span>
                            <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>{selectedCustomer.telephone}</span>
                          </div>
                          <button
                            className="btn btn-ghost btn-sm"
                            onClick={e => { e.stopPropagation(); setSelectedCustomer(null); }}
                            style={{ padding: '4px 8px', fontSize: 11 }}
                          >
                            Retirer
                          </button>
                        </div>
                      ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                          <div style={{ position: 'relative' }}>
                            <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                              className="input"
                              type="text"
                              value={customerSearch}
                              onChange={e => setCustomerSearch(e.target.value)}
                              placeholder="Rechercher client..."
                              style={{ paddingLeft: 36 }}
                              onClick={e => e.stopPropagation()}
                              onKeyDown={e => e.stopPropagation()}
                            />
                          </div>
                          {searchingCustomers && (
                            <div style={{ padding: 6, fontSize: 11, color: 'var(--text-muted)', textAlign: 'center' }}>
                              <div className="spinner" style={{ width: 14, height: 14 }} />
                              Recherche...
                            </div>
                          )}
                          {customers.length > 0 && !searchingCustomers && (
                            <div style={{
                              border: '1px solid var(--border)',
                              borderRadius: 'var(--radius-sm)',
                              background: 'white',
                              maxHeight: 150,
                              overflowY: 'auto',
                              zIndex: 20
                            }}>
                              {customers.map(customer => (
                                <div
                                  key={customer.id}
                                  onClick={e => {
                                    e.stopPropagation();
                                    setSelectedCustomer(customer);
                                    setCustomerSearch('');
                                    setCustomers([]);
                                  }}
                                  style={{
                                    padding: '8px 12px',
                                    cursor: 'pointer',
                                    borderBottom: '1px solid var(--border)',
                                    transition: 'background 0.2s'
                                  }}
                                  onMouseOver={(e) => (e.currentTarget.style.background = 'var(--bg-surface)')}
                                  onMouseOut={(e) => (e.currentTarget.style.background = 'transparent')}
                                >
                                  <div style={{ fontWeight: 600, fontSize: 12 }}>{customer.prenom} {customer.nom}</div>
                                  <div style={{ color: 'var(--text-muted)', fontSize: 11 }}>{customer.telephone}</div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                      <label style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)' }}>Montant à distribuer (F) <span style={{ color: 'var(--warning)', fontWeight: '600' }}>(Maximum 250 F)</span></label>
                      <input 
                        className="input" 
                        type="number" 
                        value={clientMontant} 
                        onChange={e => {
                          const val = e.target.value;
                          if (!val || (Number(val) > 0 && Number(val) <= 250)) {
                            setClientMontant(val);
                          }
                        }} 
                        onClick={e => e.stopPropagation()} 
                        onKeyDown={e => e.stopPropagation()} 
                        placeholder="25" 
                        min="1" 
                        max="250" 
                      />
                    </div>

                    <button
                      className="btn btn-success btn-sm"
                      style={{ justifyContent: 'center' }}
                      onClick={e => { e.stopPropagation(); handleRequestService(); }}
                      disabled={requesting}
                    >
                      {requesting ? 'Envoi...' : 'Demander cette distribution'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={{ flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden', position: 'relative', minHeight: 300 }} className={`geo-map-panel${showMap ? ' show' : ''}`}>
          <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, #0d1b2a 0%, #1a2744 50%, #0d1b2a 100%)' }}>
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={`h${i}`} style={{ position: 'absolute', left: 0, right: 0, top: `${i * 16}%`, height: 1, background: 'rgba(255,255,255,0.03)' }} />
            ))}
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={`v${i}`} style={{ position: 'absolute', top: 0, bottom: 0, left: `${i * 16}%`, width: 1, background: 'rgba(255,255,255,0.03)' }} />
            ))}
            {[
              { top: '30%', left: '10%', w: '80%' },
              { top: '60%', left: '5%', w: '70%' },
            ].map((s, i) => (
              <div key={i} style={{ position: 'absolute', top: s.top, left: s.left, width: s.w, height: 3, background: 'rgba(255,255,255,0.05)', borderRadius: 2 }} />
            ))}
            {filtered.map((partner, i) => {
              const positions = [{ top: '40%', left: '35%' }, { top: '25%', left: '58%' }, { top: '55%', left: '20%' }, { top: '70%', left: '65%' }];
              const pos = positions[i] || { top: '50%', left: '50%' };
              const isSel = selected === partner.id;
              return (
                <div key={partner.id} onClick={() => setSelected(partner.id)} style={{ position: 'absolute', top: pos.top, left: pos.left, transform: 'translate(-50%,-100%)', cursor: 'pointer', zIndex: isSel ? 10 : 1 }}>
                  <div style={{
                    background: isSel ? 'var(--primary)' : 'var(--bg-card)',
                    border: `2px solid ${isSel ? 'var(--primary)' : 'var(--border-bright)'}`,
                    borderRadius: 7,
                    padding: '4px 8px',
                    fontSize: 10,
                    fontWeight: 600,
                    color: isSel ? '#0a0f1e' : 'var(--text)',
                    boxShadow: isSel ? '0 4px 16px var(--primary-glow)' : '0 2px 6px rgba(0,0,0,0.4)',
                    whiteSpace: 'nowrap',
                    transition: 'all 0.2s',
                    transform: isSel ? 'scale(1.1)' : 'scale(1)',
                  }}>
                    <MapPin size={9} style={{ display: 'inline', marginRight: 3 }} />{partner.nomBoutique}
                  </div>
                  <div style={{ width: 6, height: 6, background: isSel ? 'var(--primary)' : 'var(--border-bright)', borderRadius: '50%', margin: '2px auto 0' }} />
                </div>
              );
            })}
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)' }}>
              <div style={{ width: 14, height: 14, background: '#3b82f6', borderRadius: '50%', border: '2.5px solid white', boxShadow: '0 0 0 5px rgba(59,130,246,0.2)', animation: 'pulse-glow 2s infinite' }} />
            </div>
          </div>
          <div style={{ position: 'absolute', top: 12, right: 12, background: 'rgba(10,15,30,0.9)', border: '1px solid var(--border)', borderRadius: 7, padding: '6px 10px', fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 5 }}>
            <div style={{ width: 8, height: 8, background: '#3b82f6', borderRadius: '50%', border: '1.5px solid white' }} />Lomé
          </div>
          {selectedPartner && (
            <div style={{ position: 'absolute', bottom: 12, left: 12, right: 12, background: 'rgba(10,15,30,0.95)', border: '1px solid var(--border-bright)', borderRadius: 'var(--radius)', padding: '12px 14px', animation: 'fadeUp 0.2s ease' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 13 }}>{selectedPartner.nomBoutique}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 1 }}>{selectedPartner.adresse}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ background: 'var(--success-dim)', color: 'var(--success)', padding: '3px 8px', borderRadius: 6, fontSize: 11, fontWeight: 700 }}>{selectedPartner.distance ?? 0} km</span>
                  <button style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 2, fontSize: 14 }} onClick={() => setSelected(null)}>✕</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      {requestMessage && (
        <div style={{ marginTop: 18, padding: 14, borderRadius: 12, background: '#141a28', border: '1px solid var(--border)', color: 'var(--text)', maxWidth: 680 }}>
          {requestMessage}
        </div>
      )}
    </div>
  );
};

export default GeolocationPage;
