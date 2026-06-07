import type { PartnerShop, User, Wallet, Transaction, FraudReport, CommissionHistory, PartnerServiceRequest } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';
const ACCESS_TOKEN_KEY = 'smartchange_access_token';
const REFRESH_TOKEN_KEY = 'smartchange_refresh_token';

const getAuthToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);
const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);
const setTokens = (access: string, refresh: string) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
};
const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    const refresh = getRefreshToken();
    if (refresh) {
      const refreshResponse = await fetch(`${API_BASE_URL}/api/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (refreshResponse.ok) {
        const data = await refreshResponse.json();
        setTokens(data.access, refresh);
        headers.Authorization = `Bearer ${data.access}`;
        const retry = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
        return handleResponse<T>(retry);
      }
    }
    clearTokens();
    throw new Error('Authentification requise');
  }

  return handleResponse<T>(response);
}

async function handleResponse<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = (payload as any).detail || (payload as any).message || 'Erreur serveur';
    throw new Error(message);
  }
  return payload as T;
}

export async function loginUser(emailOrPhone: string, password: string) {
  return apiRequest<{ success: boolean; user: User; access: string; refresh: string }>('/api/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ email_or_phone: emailOrPhone, password }),
  });
}

export async function registerUser(data: { nom: string; prenom: string; telephone: string; email: string; password: string; role: string; nom_boutique?: string; adresse?: string; latitude?: number; longitude?: number; horaires?: string }) {
  return apiRequest<{ success: boolean; user: User; access: string; refresh: string }>('/api/auth/register/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getMe() {
  return apiRequest<User>('/api/auth/me/');
}

export async function updateUserProfile(data: Partial<User>) {
  return apiRequest<User>('/api/users/me/', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function getPartners(query = '', latitude?: number, longitude?: number) {
  const params = new URLSearchParams();
  if (query) params.append('q', query);
  if (latitude) params.append('latitude', latitude.toString());
  if (longitude) params.append('longitude', longitude.toString());
  const path = `/api/partners/${params.toString() ? `?${params.toString()}` : ''}`;
  return apiRequest<PartnerShop[]>(path);
}

export interface PartnerLocation {
  id: string;
  nom: string;
  adresse: string;
  latitude: number;
  longitude: number;
  telephone?: string;
  horaires?: string;
  distance?: number;
  statut?: string;
  balance?: number;
  revenus_total?: number;
  nombre_transactions?: number;
}

export interface NearbyLocationsResponse {
  count: number;
  locations: PartnerLocation[];
}

export async function getNearbyLocations(latitude: number, longitude: number, radius?: number) {
  const params = new URLSearchParams();
  params.append('latitude', latitude.toString());
  params.append('longitude', longitude.toString());
  if (radius) params.append('radius', radius.toString());
  return apiRequest<NearbyLocationsResponse>(`/api/locations/nearby/?${params.toString()}`);
}

export async function getLocations() {
  return apiRequest<PartnerLocation[]>('/api/locations/');
}

export async function createLocation(data: Partial<PartnerLocation>) {
  return apiRequest<PartnerLocation>('/api/locations/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateLocation(id: string, data: Partial<PartnerLocation>) {
  return apiRequest<PartnerLocation>(`/api/locations/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteLocation(id: string) {
  return apiRequest<void>(`/api/locations/${id}/`, {
    method: 'DELETE',
  });
}

export async function getLocationStats(id: string) {
  return apiRequest<any>(`/api/locations/${id}/stats/`);
}

export async function requestPartnerService(payload: { partnerId: string; partnerLocationId?: number; montantService?: number; commission?: number; clientIdentifier?: string; customerId?: number; note?: string }) {
  return apiRequest<PartnerServiceRequest>('/api/partner-requests/', {
    method: 'POST',
    body: JSON.stringify({
      partnerId: Number(payload.partnerId),
      partnerLocationId: payload.partnerLocationId,
      montantService: payload.montantService ?? 25,
      commission: payload.commission ?? 25,
      clientIdentifier: payload.clientIdentifier ?? '',
      customerId: payload.customerId,
      note: payload.note ?? '',
    }),
  });
}

export async function getPartnerLocations(partnerId: string) {
  return apiRequest<PartnerLocation[]>(`/api/partners/${partnerId}/locations/`);
}

export async function getPartnerServiceRequests() {
  return apiRequest<PartnerServiceRequest[]>('/api/partner-requests/');
}

export async function acceptPartnerServiceRequest(requestId: string) {
  return apiRequest<{ success: boolean; message: string }>(`/api/partner-requests/${requestId}/accept/`, {
    method: 'POST',
  });
}

export async function completePartnerServiceRequest(requestId: string) {
  return apiRequest<{ success: boolean; message: string }>(`/api/partner-requests/${requestId}/complete/`, {
    method: 'POST',
  });
}

export async function debugAddBalance(amount: number = 100) {
  return apiRequest<{ success: boolean; message: string; wallet: Wallet }>('/api/debug/add-balance/', {
    method: 'POST',
    body: JSON.stringify({ amount }),
  });
}

export async function getWallet() {
  return apiRequest<Wallet>('/api/wallet/');
}

export interface PaymentInitResponse {
  success: boolean;
  paymentUrl?: string;
  reference?: string;
  status?: string;
  raw?: any;
}

export async function initiatePayment(payload: { amount: number; currency?: string; transactionId?: string; email?: string }) {
  return apiRequest<PaymentInitResponse>('/api/payments/initiate/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function withdrawWallet() {
  return apiRequest<{ success: boolean; withdrawn: number; wallet: Wallet }>('/api/wallet/withdraw/', {
    method: 'POST',
  });
}

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

export async function getTransactions() {
  return apiRequest<Transaction[]>('/api/transactions/');
}

export async function getCustomers(search: string = '') {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  return apiRequest<User[]>(`/api/customers/${params.toString() ? `?${params.toString()}` : ''}`);
}

export async function createTransaction(payload: { montantAchat: number; montantPaye: number; fraisService?: number; customerId?: number }) {
  return apiRequest<Transaction>('/api/transactions/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function scanQr(reference: string) {
  return apiRequest<{ status: string; message: string; reference?: string; montant?: number; expiration?: string; isFraud?: boolean }>('/api/qr/scan/', {
    method: 'POST',
    body: JSON.stringify({ reference }),
  });
}

export async function validateTransaction(transactionId: string) {
  return apiRequest<Transaction>(`/api/transactions/${transactionId}/validate/`, {
    method: 'POST',
  });
}

export async function getDashboardStats() {
  return apiRequest<{ totalTransactions: number; revenusJour: number; revenusMois: number; totalClients: number; monnaieDistribuee: number; monnaieRecuperee: number }>('/api/dashboard/');
}

export async function getAdminUsers() {
  return apiRequest<User[]>('/api/admin/users/');
}

export async function getAdminTransactions() {
  return apiRequest<Transaction[]>('/api/admin/transactions/');
}

export async function getAdminFraudReports() {
  return apiRequest<FraudReport[]>('/api/admin/fraud/');
}

export async function getAdminCommissions() {
  return apiRequest<CommissionHistory[]>('/api/admin/commissions/');
}

export function storeTokens(access: string, refresh: string) {
  setTokens(access, refresh);
}

export function logoutClient() {
  clearTokens();
}

export function getStoredToken() {
  return getAuthToken();
}
