import { DeviceStatus } from './device';

// Alarm Types
export type AlarmPriority = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type AlarmStatus = 'active' | 'acknowledged' | 'resolved' | 'dismissed';
export type AlarmCategory = 'power' | 'communication' | 'hardware' | 'system' | 'maintenance';

export interface DeviceAlarm {
  id: string;
  device_id: string;
  device_name?: string;
  
  // Alarm details
  title: string;
  description: string;
  category: AlarmCategory;
  priority: AlarmPriority;
  status: AlarmStatus;
  
  // Technical details
  alarm_code?: string;
  parameter?: string;
  threshold_value?: number;
  actual_value?: number;
  unit?: string;
  
  // Timestamps
  triggered_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  
  // User actions
  acknowledged_by?: string;
  resolved_by?: string;
  notes?: string;
  
  // Metadata
  count: number; // Numero di occorrenze
  first_occurrence: string;
  last_occurrence: string;
  
  created_at: string;
  updated_at: string;
}

export interface AlarmSummary {
  total_alarms: number;
  active_alarms: number;
  critical_alarms: number;
  high_priority_alarms: number;
  unacknowledged_alarms: number;
  
  alarms_by_priority: Record<AlarmPriority, number>;
  alarms_by_category: Record<AlarmCategory, number>;
  alarms_by_device: Array<{
    device_id: string;
    device_name: string;
    alarm_count: number;
  }>;
}

// Alarm Filters
export interface AlarmFilters {
  device_id?: string[];
  priority?: AlarmPriority[];
  status?: AlarmStatus[];
  category?: AlarmCategory[];
  date_from?: string;
  date_to?: string;
  search?: string;
}

// Notification Types (per WebSocket)
export interface AlarmNotification {
  type: 'new_alarm' | 'alarm_acknowledged' | 'alarm_resolved';
  alarm: DeviceAlarm;
  timestamp: string;
}

export interface AlarmAction {
  action: 'acknowledge' | 'resolve' | 'dismiss';
  alarm_id: string;
  user_id: string;
  notes?: string;
  timestamp: string;
} 