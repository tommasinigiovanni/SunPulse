// Device Types
export type DeviceType = 'inverter' | 'battery' | 'meter' | 'sensor' | 'gateway';
export type DeviceStatus = 'online' | 'offline' | 'warning' | 'maintenance' | 'error';

export interface Device {
  id: string;
  name: string;
  type: DeviceType;
  status: DeviceStatus;
  serial_number: string;
  model?: string;
  manufacturer?: string;
  installation_date?: string;
  location?: string;
  
  // Dati real-time
  current_power?: number;
  daily_energy?: number;
  total_energy?: number;
  
  // Metadati
  last_seen?: string;
  firmware_version?: string;
  configuration?: DeviceConfiguration;
  // alarms?: DeviceAlarm[]; // Temporarily commented - needs import
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface DeviceConfiguration {
  id: string;
  device_id: string;
  rated_power?: number;
  max_voltage?: number;
  max_current?: number;
  efficiency?: number;
  
  // Configurazioni specifiche
  settings: Record<string, any>;
  
  created_at: string;
  updated_at: string;
}

// Real-time Data Types
export interface RealTimeData {
  device_id: string;
  timestamp: string;
  
  // Power data
  power?: number;
  voltage?: number;
  current?: number;
  frequency?: number;
  
  // Energy data
  energy_today?: number;
  energy_total?: number;
  
  // Battery data (se applicabile)
  battery_level?: number;
  battery_voltage?: number;
  battery_current?: number;
  battery_temperature?: number;
  
  // Environmental data
  temperature?: number;
  humidity?: number;
  irradiance?: number;
  
  // System data
  efficiency?: number;
  status: DeviceStatus;
}

export interface HistoricalData {
  device_id: string;
  timestamp: string;
  value: number;
  parameter: string; // 'power', 'energy', 'voltage', etc.
  unit: string;
}

// Chart Data Types
export interface ChartDataPoint {
  timestamp: string;
  value: number;
  type?: string;
  color?: string;
}

export interface PowerChartData {
  timestamp: string;
  production: number;
  consumption: number;
  grid: number;
  battery?: number;
}

export interface EnergyChartData {
  timestamp: string;
  energy: number;
  device_id: string;
  device_name: string;
}

// Device Summary Types
export interface DeviceSummary {
  total_devices: number;
  online_devices: number;
  offline_devices: number;
  warning_devices: number;
  
  total_power: number;
  daily_energy: number;
  monthly_energy: number;
  yearly_energy: number;
  
  efficiency: number;
  co2_saved: number;
  money_saved: number;
}

// Device Filters
export interface DeviceFilters {
  type?: DeviceType[];
  status?: DeviceStatus[];
  location?: string[];
  manufacturer?: string[];
  search?: string;
  date_from?: string;
  date_to?: string;
} 