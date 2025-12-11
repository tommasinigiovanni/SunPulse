// API Endpoints
export const API_ENDPOINTS = {
  DEVICES: '/devices',
  REALTIME: '/devices/realtime',
  HISTORY: '/devices/{id}/history',
  ALARMS: '/alarms',
  DEVICE_ALARMS: '/devices/{id}/alarms',
  ANALYTICS: '/analytics',
  HEALTH: '/health',
} as const;

// WebSocket Eventi
export const WS_EVENTS = {
  REALTIME_UPDATE: 'realtime_update',
  DEVICE_STATUS: 'device_status',
  NEW_ALARM: 'new_alarm',
  ALARM_RESOLVED: 'alarm_resolved',
  CONNECTION_STATUS: 'connection_status',
} as const;

// Tipi di dispositivo
export const DEVICE_TYPES = {
  INVERTER: 'inverter',
  BATTERY: 'battery', 
  METER: 'meter',
  SENSOR: 'sensor',
  GATEWAY: 'gateway',
} as const;

// Stati dispositivo
export const DEVICE_STATUS = {
  ONLINE: 'online',
  OFFLINE: 'offline',
  WARNING: 'warning',
  MAINTENANCE: 'maintenance',
  ERROR: 'error',
} as const;

// Configurazione grafici
export const CHART_CONFIG = {
  COLORS: {
    PRIMARY: '#1890ff',
    SUCCESS: '#52c41a',
    WARNING: '#faad14',
    ERROR: '#ff4d4f',
    INFO: '#13c2c2',
  },
  HEIGHT: {
    SMALL: 200,
    MEDIUM: 300,
    LARGE: 400,
    EXTRA_LARGE: 500,
  },
  ANIMATION_DURATION: 1000,
};

// Intervalli di aggiornamento
export const UPDATE_INTERVALS = {
  REALTIME: 30000, // 30 secondi
  DEVICES: 60000, // 1 minuto
  ANALYTICS: 300000, // 5 minuti
};

// Configurazione notifiche
export const NOTIFICATION_CONFIG = {
  DURATION: 4.5,
  PLACEMENT: 'topRight' as const,
  MAX_COUNT: 3,
};

// Priorità allarmi
export const ALARM_PRIORITY = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
  INFO: 'info',
} as const;

// Duplicate removed - keeping the original definitions above

// Dimensioni responsive
export const BREAKPOINTS = {
  XS: 480,
  SM: 576,
  MD: 768,
  LG: 992,
  XL: 1200,
  XXL: 1600,
} as const;

// Formati data
export const DATE_FORMATS = {
  DATE: 'DD/MM/YYYY',
  TIME: 'HH:mm',
  DATETIME: 'DD/MM/YYYY HH:mm',
  DATETIME_FULL: 'DD/MM/YYYY HH:mm:ss',
  CHART_HOUR: 'HH:mm',
  CHART_DAY: 'DD/MM',
  CHART_MONTH: 'MMM YYYY',
} as const;

// Periodi analytics
export const ANALYTICS_PERIODS = {
  DAY: 'day',
  WEEK: 'week',
  MONTH: 'month',
  YEAR: 'year',
} as const;

// Configurazione cache
export const CACHE_KEYS = {
  DEVICES: 'devices',
  REALTIME_DATA: 'realtime_data',
  ANALYTICS: 'analytics',
  USER_PREFERENCES: 'user_preferences',
} as const;

export const CACHE_TTL = {
  SHORT: 30000,    // 30 secondi
  MEDIUM: 300000,  // 5 minuti  
  LONG: 1800000,   // 30 minuti
} as const;

// Messaggi di errore
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Errore di connessione. Verifica la tua connessione internet.',
  AUTH_ERROR: 'Errore di autenticazione. Effettua nuovamente il login.',
  PERMISSION_ERROR: 'Non hai i permessi necessari per questa operazione.',
  NOT_FOUND: 'La risorsa richiesta non è stata trovata.',
  SERVER_ERROR: 'Errore interno del server. Riprova più tardi.',
  VALIDATION_ERROR: 'I dati inseriti non sono validi.',
  UNKNOWN_ERROR: 'Si è verificato un errore imprevisto.',
} as const;

// Duplicate removed - keeping the original definition above

// Configurazione layout
export const LAYOUT_CONFIG = {
  SIDEBAR_WIDTH: 250,
  SIDEBAR_COLLAPSED_WIDTH: 80,
  HEADER_HEIGHT: 64,
  CONTENT_PADDING: 24,
} as const;

// Permissions
export const PERMISSIONS = {
  READ_DEVICES: 'read:devices',
  WRITE_DEVICES: 'write:devices',
  READ_ANALYTICS: 'read:analytics',
  MANAGE_USERS: 'manage:users',
  ADMIN: 'admin',
} as const;

// Roles
export const ROLES = {
  ADMIN: 'admin',
  OPERATOR: 'operator',
  VIEWER: 'viewer',
} as const; 