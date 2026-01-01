/**
 * ZCS (Zero Config Setup) TypeScript Types
 *
 * Types for integration with the ZCS API and device management system.
 * These types define the structure of data received from ZCS devices and
 * how it maps to the internal SunPulse data model.
 */

// ============================================================================
// ZCS Device Types
// ============================================================================

/**
 * ZCS Device Type Enumeration
 */
export type ZCSDeviceType =
  | 'inverter'
  | 'battery'
  | 'meter'
  | 'sensor'
  | 'gateway'
  | 'hybrid'
  | 'optimizer';

/**
 * ZCS Device Status from API
 */
export type ZCSDeviceStatus =
  | 'online'
  | 'offline'
  | 'standby'
  | 'fault'
  | 'warning'
  | 'maintenance';

/**
 * Main ZCS Device Structure
 */
export interface ZCSDevice {
  thing_key: string;              // Unique identifier (primary key in ZCS)
  thing_name: string;             // Human-readable name
  type: ZCSDeviceType;            // Device type
  status: ZCSDeviceStatus;        // Current status
  serial_number: string;          // Serial number
  firmware_version?: string;      // Firmware version
  model?: string;                 // Device model
  manufacturer?: string;          // Manufacturer name
  installation_date?: string;     // ISO date string
  last_communication?: string;    // ISO date string
  location?: ZCSLocation;         // Physical location
  configuration?: ZCSConfiguration; // Device configuration
  metadata?: Record<string, any>; // Additional metadata
}

/**
 * ZCS Device Location
 */
export interface ZCSLocation {
  latitude?: number;
  longitude?: number;
  address?: string;
  site_name?: string;
  zone?: string;
}

/**
 * ZCS Device Configuration
 */
export interface ZCSConfiguration {
  rated_power?: number;           // Rated power in kW
  max_power?: number;             // Maximum power in kW
  min_power?: number;             // Minimum power in kW
  voltage_range?: {
    min: number;
    max: number;
  };
  current_range?: {
    min: number;
    max: number;
  };
  operating_temperature?: {
    min: number;
    max: number;
  };
  polling_interval?: number;      // Polling interval in seconds
  data_retention?: number;        // Data retention in days
  alarm_thresholds?: ZCSAlarmThresholds;
  custom_settings?: Record<string, any>;
}

// ============================================================================
// ZCS Real-Time Data
// ============================================================================

/**
 * ZCS Real-Time Data Point
 */
export interface ZCSRealTimeData {
  thing_key: string;              // Device identifier
  timestamp: string;              // ISO timestamp
  measurements: ZCSMeasurements;  // Measurement data
  status: ZCSDeviceStatus;        // Current status
  quality?: ZCSDataQuality;       // Data quality indicator
}

/**
 * ZCS Measurements Structure
 */
export interface ZCSMeasurements {
  // Power measurements (W)
  power_active?: number;
  power_reactive?: number;
  power_apparent?: number;

  // Energy measurements (kWh)
  energy_import?: number;
  energy_export?: number;
  energy_generated?: number;
  energy_consumed?: number;

  // Electrical measurements
  voltage_l1?: number;
  voltage_l2?: number;
  voltage_l3?: number;
  current_l1?: number;
  current_l2?: number;
  current_l3?: number;
  frequency?: number;
  power_factor?: number;

  // Battery specific
  battery_voltage?: number;
  battery_current?: number;
  battery_soc?: number;            // State of Charge (%)
  battery_soh?: number;            // State of Health (%)
  battery_temperature?: number;

  // Inverter specific
  dc_voltage?: number;
  dc_current?: number;
  dc_power?: number;
  ac_voltage?: number;
  ac_current?: number;
  ac_power?: number;
  inverter_temperature?: number;
  inverter_efficiency?: number;    // (%)

  // Environmental
  ambient_temperature?: number;
  irradiance?: number;             // W/m²

  // Additional metrics
  [key: string]: number | string | boolean | undefined;
}

/**
 * ZCS Data Quality Indicator
 */
export interface ZCSDataQuality {
  valid: boolean;
  accuracy?: number;               // Percentage
  completeness?: number;           // Percentage
  timeliness?: number;             // Seconds since measurement
  flags?: string[];                // Quality flags
}

// ============================================================================
// ZCS Alarms
// ============================================================================

/**
 * ZCS Alarm Severity Levels
 */
export type ZCSAlarmSeverity =
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'
  | 'info';

/**
 * ZCS Alarm Categories
 */
export type ZCSAlarmCategory =
  | 'power'
  | 'communication'
  | 'hardware'
  | 'software'
  | 'environmental'
  | 'maintenance'
  | 'security';

/**
 * ZCS Alarm Code Structure
 */
export interface ZCSAlarmCode {
  code: string;                    // Alarm code (e.g., "PWR-001")
  category: ZCSAlarmCategory;
  severity: ZCSAlarmSeverity;
  description: string;
  recommended_action?: string;
  auto_resolve?: boolean;
}

/**
 * ZCS Alarm Event
 */
export interface ZCSAlarm {
  alarm_id: string;                // Unique alarm ID
  thing_key: string;               // Device identifier
  alarm_code: string;              // Alarm code
  category: ZCSAlarmCategory;
  severity: ZCSAlarmSeverity;
  status: 'active' | 'acknowledged' | 'resolved';
  title: string;
  description: string;
  triggered_at: string;            // ISO timestamp
  acknowledged_at?: string;        // ISO timestamp
  resolved_at?: string;            // ISO timestamp
  acknowledged_by?: string;        // User ID
  resolved_by?: string;            // User ID
  occurrences: number;             // Number of occurrences
  first_occurrence: string;        // ISO timestamp
  last_occurrence: string;         // ISO timestamp
  affected_parameters?: string[];  // List of affected parameters
  threshold?: {
    parameter: string;
    threshold_value: number;
    actual_value: number;
    operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte';
  };
  metadata?: Record<string, any>;
}

/**
 * ZCS Alarm Thresholds Configuration
 */
export interface ZCSAlarmThresholds {
  power?: {
    max?: number;
    min?: number;
  };
  voltage?: {
    max?: number;
    min?: number;
  };
  current?: {
    max?: number;
    min?: number;
  };
  temperature?: {
    max?: number;
    min?: number;
  };
  battery_soc?: {
    max?: number;
    min?: number;
  };
  custom?: Record<string, {
    max?: number;
    min?: number;
    operator?: 'gt' | 'lt' | 'eq' | 'gte' | 'lte';
  }>;
}

// ============================================================================
// ZCS Historical Data
// ============================================================================

/**
 * ZCS Historical Data Query Parameters
 */
export interface ZCSHistoricalQuery {
  thing_keys: string[];            // Device identifiers
  parameters: string[];            // Parameters to query
  start_time: string;              // ISO timestamp
  end_time: string;                // ISO timestamp
  aggregation?: ZCSAggregation;
  resolution?: number;             // Seconds
  limit?: number;
  offset?: number;
}

/**
 * ZCS Data Aggregation Types
 */
export type ZCSAggregation =
  | 'raw'
  | 'avg'
  | 'min'
  | 'max'
  | 'sum'
  | 'count'
  | 'first'
  | 'last';

/**
 * ZCS Historical Data Point
 */
export interface ZCSHistoricalDataPoint {
  thing_key: string;
  timestamp: string;
  parameter: string;
  value: number;
  unit?: string;
  quality?: ZCSDataQuality;
}

/**
 * ZCS Historical Data Response
 */
export interface ZCSHistoricalDataResponse {
  thing_key: string;
  parameter: string;
  data_points: ZCSHistoricalDataPoint[];
  aggregation?: ZCSAggregation;
  resolution?: number;
  unit?: string;
  statistics?: {
    count: number;
    min: number;
    max: number;
    avg: number;
    sum: number;
  };
}

// ============================================================================
// ZCS API Response Types
// ============================================================================

/**
 * Generic ZCS API Response
 */
export interface ZCSApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ZCSApiError;
  timestamp: string;
  request_id?: string;
}

/**
 * ZCS API Error
 */
export interface ZCSApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  trace_id?: string;
}

/**
 * ZCS Paginated Response
 */
export interface ZCSPaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// ============================================================================
// ZCS WebSocket Messages
// ============================================================================

/**
 * ZCS WebSocket Event Types
 */
export type ZCSWebSocketEventType =
  | 'device.status'
  | 'device.data'
  | 'device.alarm'
  | 'device.config'
  | 'system.notification'
  | 'connection.heartbeat';

/**
 * ZCS WebSocket Message
 */
export interface ZCSWebSocketMessage {
  event: ZCSWebSocketEventType;
  thing_key?: string;
  data: any;
  timestamp: string;
  sequence?: number;
}

/**
 * ZCS Device Status Update Message
 */
export interface ZCSDeviceStatusMessage extends ZCSWebSocketMessage {
  event: 'device.status';
  data: {
    thing_key: string;
    status: ZCSDeviceStatus;
    previous_status?: ZCSDeviceStatus;
    reason?: string;
  };
}

/**
 * ZCS Real-Time Data Message
 */
export interface ZCSDataMessage extends ZCSWebSocketMessage {
  event: 'device.data';
  data: ZCSRealTimeData;
}

/**
 * ZCS Alarm Message
 */
export interface ZCSAlarmMessage extends ZCSWebSocketMessage {
  event: 'device.alarm';
  data: {
    action: 'triggered' | 'acknowledged' | 'resolved';
    alarm: ZCSAlarm;
  };
}

// ============================================================================
// Mapping Types (ZCS <-> SunPulse Internal)
// ============================================================================

/**
 * Device Type Mapping
 */
export const ZCS_DEVICE_TYPE_MAPPING: Record<ZCSDeviceType, string> = {
  inverter: 'inverter',
  battery: 'battery',
  meter: 'meter',
  sensor: 'sensor',
  gateway: 'gateway',
  hybrid: 'inverter',
  optimizer: 'sensor',
};

/**
 * Status Mapping
 */
export const ZCS_STATUS_MAPPING: Record<ZCSDeviceStatus, string> = {
  online: 'online',
  offline: 'offline',
  standby: 'maintenance',
  fault: 'error',
  warning: 'warning',
  maintenance: 'maintenance',
};

/**
 * Alarm Severity Mapping
 */
export const ZCS_ALARM_SEVERITY_MAPPING: Record<ZCSAlarmSeverity, string> = {
  critical: 'critical',
  high: 'high',
  medium: 'medium',
  low: 'low',
  info: 'info',
};

/**
 * Common ZCS Alarm Codes Reference
 */
export const ZCS_COMMON_ALARM_CODES: Record<string, ZCSAlarmCode> = {
  'PWR-001': {
    code: 'PWR-001',
    category: 'power',
    severity: 'high',
    description: 'Overvoltage detected',
    recommended_action: 'Check grid voltage and inverter configuration',
    auto_resolve: true,
  },
  'PWR-002': {
    code: 'PWR-002',
    category: 'power',
    severity: 'high',
    description: 'Undervoltage detected',
    recommended_action: 'Check grid connection and voltage levels',
    auto_resolve: true,
  },
  'PWR-003': {
    code: 'PWR-003',
    category: 'power',
    severity: 'critical',
    description: 'Overcurrent detected',
    recommended_action: 'Immediately check wiring and connections',
    auto_resolve: false,
  },
  'COM-001': {
    code: 'COM-001',
    category: 'communication',
    severity: 'medium',
    description: 'Communication timeout',
    recommended_action: 'Check network connection and device status',
    auto_resolve: true,
  },
  'COM-002': {
    code: 'COM-002',
    category: 'communication',
    severity: 'low',
    description: 'Weak signal strength',
    recommended_action: 'Check antenna and network quality',
    auto_resolve: true,
  },
  'HW-001': {
    code: 'HW-001',
    category: 'hardware',
    severity: 'critical',
    description: 'Hardware fault detected',
    recommended_action: 'Contact technical support for inspection',
    auto_resolve: false,
  },
  'TEMP-001': {
    code: 'TEMP-001',
    category: 'environmental',
    severity: 'high',
    description: 'Temperature threshold exceeded',
    recommended_action: 'Ensure proper ventilation and cooling',
    auto_resolve: true,
  },
  'BAT-001': {
    code: 'BAT-001',
    category: 'power',
    severity: 'medium',
    description: 'Low battery state of charge',
    recommended_action: 'Battery SOC below configured threshold',
    auto_resolve: true,
  },
  'BAT-002': {
    code: 'BAT-002',
    category: 'hardware',
    severity: 'high',
    description: 'Battery health degraded',
    recommended_action: 'Schedule battery maintenance or replacement',
    auto_resolve: false,
  },
};

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard for ZCS Device
 */
export function isZCSDevice(obj: any): obj is ZCSDevice {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.thing_key === 'string' &&
    typeof obj.thing_name === 'string' &&
    typeof obj.type === 'string'
  );
}

/**
 * Type guard for ZCS Alarm
 */
export function isZCSAlarm(obj: any): obj is ZCSAlarm {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.alarm_id === 'string' &&
    typeof obj.thing_key === 'string' &&
    typeof obj.alarm_code === 'string'
  );
}

/**
 * Type guard for ZCS Real-Time Data
 */
export function isZCSRealTimeData(obj: any): obj is ZCSRealTimeData {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.thing_key === 'string' &&
    typeof obj.timestamp === 'string' &&
    typeof obj.measurements === 'object'
  );
}
