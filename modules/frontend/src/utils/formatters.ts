import dayjs from 'dayjs';
import 'dayjs/locale/it';
import relativeTime from 'dayjs/plugin/relativeTime';
import localizedFormat from 'dayjs/plugin/localizedFormat';

// Configura dayjs
dayjs.extend(relativeTime);
dayjs.extend(localizedFormat);
dayjs.locale('it');

// Formattazione energia
export const formatPower = (watts: number, precision: number = 0): string => {
  if (watts >= 1000000) {
    return `${(watts / 1000000).toFixed(precision)} MW`;
  } else if (watts >= 1000) {
    return `${(watts / 1000).toFixed(precision)} kW`;
  }
  return `${watts.toFixed(precision)} W`;
};

export const formatEnergy = (wattHours: number, precision: number = 2): string => {
  if (wattHours >= 1000000) {
    return `${(wattHours / 1000000).toFixed(precision)} MWh`;
  } else if (wattHours >= 1000) {
    return `${(wattHours / 1000).toFixed(precision)} kWh`;
  }
  return `${wattHours.toFixed(precision)} Wh`;
};

// Formattazione valuta
export const formatCurrency = (amount: number, currency: string = 'EUR'): string => {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: currency,
  }).format(amount);
};

// Formattazione percentuale
export const formatPercentage = (value: number, precision: number = 1): string => {
  return `${value.toFixed(precision)}%`;
};

// Formattazione CO2
export const formatCO2 = (kg: number, precision: number = 1): string => {
  if (kg >= 1000) {
    return `${(kg / 1000).toFixed(precision)} t CO₂`;
  }
  return `${kg.toFixed(precision)} kg CO₂`;
};

// Formattazione date
export const formatDate = (date: string | Date, format: string = 'DD/MM/YYYY'): string => {
  return dayjs(date).format(format);
};

export const formatDateTime = (date: string | Date): string => {
  return dayjs(date).format('DD/MM/YYYY HH:mm');
};

export const formatTime = (date: string | Date): string => {
  return dayjs(date).format('HH:mm');
};

export const formatRelativeTime = (date: string | Date): string => {
  return dayjs(date).fromNow();
};

// Formattazione numeri
export const formatNumber = (value: number, precision: number = 0): string => {
  return new Intl.NumberFormat('it-IT', {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
  }).format(value);
};

// Formattazione stato dispositivo
export const formatDeviceStatus = (status: string): { text: string; color: string } => {
  const statusMap: Record<string, { text: string; color: string }> = {
    online: { text: 'Online', color: '#52c41a' },
    offline: { text: 'Offline', color: '#ff4d4f' },
    warning: { text: 'Attenzione', color: '#faad14' },
    maintenance: { text: 'Manutenzione', color: '#722ed1' },
    error: { text: 'Errore', color: '#ff4d4f' },
  };
  
  return statusMap[status] || { text: status, color: '#d9d9d9' };
};

// Formattazione tipo dispositivo
export const formatDeviceType = (type: string): string => {
  const typeMap: Record<string, string> = {
    inverter: 'Inverter',
    battery: 'Batteria',
    meter: 'Contatore',
    sensor: 'Sensore',
    gateway: 'Gateway',
  };
  
  return typeMap[type] || type;
};

// Formattazione priorità allarme
export const formatAlarmPriority = (priority: string): { text: string; color: string } => {
  const priorityMap: Record<string, { text: string; color: string }> = {
    critical: { text: 'Critico', color: '#ff4d4f' },
    high: { text: 'Alto', color: '#fa8c16' },
    medium: { text: 'Medio', color: '#faad14' },
    low: { text: 'Basso', color: '#52c41a' },
    info: { text: 'Info', color: '#1890ff' },
  };
  
  return priorityMap[priority] || { text: priority, color: '#d9d9d9' };
};

// Utility per colori grafici
export const getChartColor = (index: number): string => {
  const colors = [
    '#1890ff', // Blu
    '#52c41a', // Verde
    '#faad14', // Arancione
    '#f5222d', // Rosso
    '#722ed1', // Viola
    '#fa8c16', // Arancione scuro
    '#eb2f96', // Rosa
    '#13c2c2', // Ciano
  ];
  
  return colors[index % colors.length];
};

// Validazione dati
export const isValidNumber = (value: any): boolean => {
  return typeof value === 'number' && !isNaN(value) && isFinite(value);
};

export const isValidDate = (date: any): boolean => {
  return dayjs(date).isValid();
}; 