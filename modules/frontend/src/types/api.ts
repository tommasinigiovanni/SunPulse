import { Device, DeviceType, DeviceStatus, DeviceConfiguration, RealTimeData, HistoricalData } from './device';
import { DeviceAlarm } from './alarm';

// Re-export RealTimeData for convenience
export type { RealTimeData } from './device';

// Base API Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface ApiError {
  error: string;
  message: string;
  status_code: number;
  details?: Record<string, any>;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginationParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// Device API Types
export interface DeviceListResponse extends PaginatedResponse<Device> {}

export interface RealTimeDataResponse {
  devices: RealTimeData[];
  timestamp: string;
  summary: {
    total_power: number;
    total_energy_today: number;
    online_devices: number;
    total_devices: number;
  };
}

export interface HistoricalDataResponse {
  device_id: string;
  parameter: string;
  data_points: HistoricalData[];
  start_date: string;
  end_date: string;
  summary: {
    min_value: number;
    max_value: number;
    avg_value: number;
    total_value?: number;
  };
}

// Analytics API Types
export interface AnalyticsResponse {
  period: 'day' | 'week' | 'month' | 'year';
  start_date: string;
  end_date: string;
  
  energy_production: {
    total: number;
    by_device: Array<{
      device_id: string;
      device_name: string;
      energy: number;
    }>;
    timeline: Array<{
      timestamp: string;
      energy: number;
    }>;
  };
  
  energy_consumption: {
    total: number;
    timeline: Array<{
      timestamp: string;
      consumption: number;
    }>;
  };
  
  efficiency: {
    average: number;
    timeline: Array<{
      timestamp: string;
      efficiency: number;
    }>;
  };
  
  environmental_impact: {
    co2_saved: number;
    trees_equivalent: number;
    money_saved: number;
  };
  
  performance_indicators: {
    uptime: number;
    availability: number;
    capacity_factor: number;
  };
}

// Health Check Types
export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  uptime: number;
  
  services: {
    database: ServiceHealth;
    redis: ServiceHealth;
    influxdb: ServiceHealth;
    external_api: ServiceHealth;
  };
  
  metrics: {
    active_connections: number;
    memory_usage: number;
    cpu_usage: number;
    response_time: number;
  };
}

export interface ServiceHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  response_time?: number;
  last_check: string;
  error?: string;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: string;
}

export interface RealTimeUpdateMessage extends WebSocketMessage {
  type: 'realtime_update';
  payload: RealTimeData;
}

export interface DeviceStatusMessage extends WebSocketMessage {
  type: 'device_status';
  payload: {
    device_id: string;
    status: DeviceStatus;
    previous_status: DeviceStatus;
  };
}

export interface AlarmMessage extends WebSocketMessage {
  type: 'new_alarm' | 'alarm_resolved';
  payload: DeviceAlarm;
}

// Request Types
export interface CreateDeviceRequest {
  name: string;
  type: DeviceType;
  serial_number: string;
  model?: string;
  manufacturer?: string;
  location?: string;
  configuration?: Partial<DeviceConfiguration>;
}

export interface UpdateDeviceRequest {
  name?: string;
  location?: string;
  configuration?: Partial<DeviceConfiguration>;
}

export interface AlarmActionRequest {
  action: 'acknowledge' | 'resolve' | 'dismiss';
  notes?: string;
}

// Chart Data Request Types
export interface ChartDataRequest {
  device_ids?: string[];
  start_date: string;
  end_date: string;
  parameters: string[];
  granularity: 'minute' | 'hour' | 'day' | 'week' | 'month';
} 