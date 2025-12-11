import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Crea l'istanza axios
export const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Store per il token (sarà settato dal hook useAuth)
let authTokenGetter: (() => Promise<string | null>) | null = null;

export const setAuthTokenGetter = (getter: () => Promise<string | null>) => {
  authTokenGetter = getter;
};

// Request interceptor per aggiungere il token
axiosInstance.interceptors.request.use(
  async (config) => {
    try {
      if (authTokenGetter) {
        const token = await authTokenGetter();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
    } catch (error) {
      console.warn('Errore nel recupero del token di autenticazione:', error);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor per gestire errori comuni
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // Gestione errori comuni
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          console.error('Non autorizzato - effettua il login');
          // Qui potresti triggerare un redirect al login
          break;
        case 403:
          console.error('Accesso negato - permessi insufficienti');
          break;
        case 404:
          console.error('Risorsa non trovata');
          break;
        case 422:
          console.error('Dati non validi:', data);
          break;
        case 500:
          console.error('Errore interno del server');
          break;
        default:
          console.error(`Errore API (${status}):`, data);
      }
    } else if (error.request) {
      console.error('Errore di rete - verifica la connessione');
    } else {
      console.error('Errore nella configurazione della richiesta:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Utility functions per chiamate API specifiche
export const apiClient = {
  // Devices
  async getDevices(params?: any) {
    const response = await axiosInstance.get('/devices', { params });
    return response.data;
  },
  
  async getDevice(id: string) {
    const response = await axiosInstance.get(`/devices/${id}`);
    return response.data;
  },
  
  async getRealTimeData(deviceIds?: string[]) {
    const params = deviceIds ? { device_ids: deviceIds.join(',') } : {};
    const response = await axiosInstance.get('/data/realtime', { params });
    return response.data;
  },
  
  async getHistoricalData(deviceId: string, startDate: string, endDate: string) {
    const response = await axiosInstance.get(`/devices/${deviceId}/historic`, {
      params: { start: startDate, end: endDate }
    });
    return response.data;
  },
  
  // Alarms
  async getAlarms(deviceId?: string) {
    const url = deviceId ? `/devices/${deviceId}/alarms` : '/alarms';
    const response = await axiosInstance.get(url);
    return response.data;
  },
  
  // Analytics
  async getAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'day') {
    const response = await axiosInstance.get('/analytics', {
      params: { period }
    });
    return response.data;
  },
  
  // Health check
  async healthCheck() {
    const response = await axiosInstance.get('/health');
    return response.data;
  },
}; 