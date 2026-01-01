import React from 'react';
import { Card, Badge, Tooltip, Button, Space, Typography, Statistic } from 'antd';
import {
  ControlOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  ToolOutlined
} from '@ant-design/icons';
import { Device } from '@/types/device';
import { DeviceAlarm, AlarmPriority } from '@/types/alarm';
import { formatPower, formatEnergy, formatDeviceStatus, formatDeviceType, formatRelativeTime } from '@/utils/formatters';

const { Text, Title } = Typography;

interface DeviceCardProps {
  device: Device;
  onClick?: (device: Device) => void;
  showActions?: boolean;
  compact?: boolean;
}

export const DeviceCard: React.FC<DeviceCardProps> = ({
  device,
  onClick,
  showActions = true,
  compact = false
}) => {
  const statusInfo = formatDeviceStatus(device.status);
  const typeLabel = formatDeviceType(device.type);

  const getStatusIcon = () => {
    switch (device.status) {
      case 'online':
        return <CheckCircleOutlined style={{ color: statusInfo.color }} />;
      case 'offline':
        return <CloseCircleOutlined style={{ color: statusInfo.color }} />;
      case 'warning':
        return <ExclamationCircleOutlined style={{ color: statusInfo.color }} />;
      case 'maintenance':
        return <ToolOutlined style={{ color: statusInfo.color }} />;
      default:
        return <CloseCircleOutlined style={{ color: statusInfo.color }} />;
    }
  };

  // Helper functions for alarm styling
  const getHighestAlarmPriority = (alarms: DeviceAlarm[]): AlarmPriority => {
    const priorities: AlarmPriority[] = ['critical', 'high', 'medium', 'low', 'info'];
    for (const priority of priorities) {
      if (alarms.some(alarm => alarm.priority === priority && alarm.status === 'active')) {
        return priority;
      }
    }
    return 'info';
  };

  const getAlarmBackgroundColor = (alarms: DeviceAlarm[]): string => {
    const highestPriority = getHighestAlarmPriority(alarms);
    switch (highestPriority) {
      case 'critical':
        return '#fff1f0';
      case 'high':
        return '#fff2e8';
      case 'medium':
        return '#fffbe6';
      case 'low':
        return '#f6ffed';
      default:
        return '#f0f5ff';
    }
  };

  const getAlarmBorderColor = (alarms: DeviceAlarm[]): string => {
    const highestPriority = getHighestAlarmPriority(alarms);
    switch (highestPriority) {
      case 'critical':
        return '#ffccc7';
      case 'high':
        return '#ffbb96';
      case 'medium':
        return '#ffe58f';
      case 'low':
        return '#b7eb8f';
      default:
        return '#adc6ff';
    }
  };

  const getAlarmIconColor = (alarms: DeviceAlarm[]): string => {
    const highestPriority = getHighestAlarmPriority(alarms);
    switch (highestPriority) {
      case 'critical':
        return '#cf1322';
      case 'high':
        return '#fa8c16';
      case 'medium':
        return '#faad14';
      case 'low':
        return '#52c41a';
      default:
        return '#1890ff';
    }
  };

  const cardTitle = (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 0, flex: 1 }}>
        <Tooltip title={device.name}>
          <Text 
            strong 
            ellipsis 
            style={{ fontSize: compact ? 14 : 16, maxWidth: 120 }}
          >
            {device.name}
          </Text>
        </Tooltip>
        {getStatusIcon()}
      </div>
    </div>
  );

  const cardExtra = showActions ? (
    <Tooltip title="Visualizza dettagli">
      <Button 
        type="link" 
        icon={<ControlOutlined />} 
        onClick={(e) => {
          e.stopPropagation();
          onClick?.(device);
        }}
        size={compact ? 'small' : 'middle'}
      >
        {!compact && 'Dettagli'}
      </Button>
    </Tooltip>
  ) : null;

  const handleCardClick = () => {
    onClick?.(device);
  };

  return (
    <Card
      size={compact ? 'small' : 'default'}
      title={cardTitle}
      extra={cardExtra}
      hoverable={!!onClick}
      onClick={handleCardClick}
      style={{ 
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        borderColor: device.status === 'offline' ? '#ff4d4f' : undefined,
      }}
      bodyStyle={{ 
        padding: compact ? 12 : 24 
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: compact ? 8 : 12 }}>
        {/* Device Info */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Text type="secondary" style={{ fontSize: compact ? 11 : 12 }}>
            {typeLabel}
          </Text>
          <Text type="secondary" style={{ fontSize: compact ? 11 : 12 }}>
            {device.serial_number}
          </Text>
        </div>

        {/* Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: compact ? 8 : 16 }}>
          <Statistic
            title="Potenza Attuale"
            value={device.current_power || 0}
            formatter={(value) => formatPower(Number(value))}
            valueStyle={{ 
              fontSize: compact ? 14 : 16,
              color: device.current_power && device.current_power > 0 ? '#1890ff' : '#d9d9d9' 
            }}
          />
          
          <Statistic
            title="Energia Oggi"
            value={device.daily_energy || 0}
            precision={2}
            suffix="kWh"
            valueStyle={{ 
              fontSize: compact ? 14 : 16,
              color: '#52c41a' 
            }}
          />
        </div>

        {/* Additional Info */}
        {!compact && (
          <div style={{ marginTop: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                Energia Totale:
              </Text>
              <Text style={{ fontSize: 12 }}>
                {formatEnergy((device.total_energy || 0) * 1000)}
              </Text>
            </div>
            
            {device.location && (
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Posizione:
                </Text>
                <Text style={{ fontSize: 12 }}>
                  {device.location}
                </Text>
              </div>
            )}

            {device.last_seen && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Ultimo aggiornamento:
                </Text>
                <Text style={{ fontSize: 12 }}>
                  {formatRelativeTime(device.last_seen)}
                </Text>
              </div>
            )}
          </div>
        )}

        {/* Alarms Display */}
        {device.alarms && device.alarms.length > 0 && (
          <div style={{
            marginTop: compact ? 4 : 8,
            padding: compact ? 6 : 10,
            background: getAlarmBackgroundColor(device.alarms),
            borderRadius: 4,
            border: `1px solid ${getAlarmBorderColor(device.alarms)}`
          }}>
            <Space size="small" style={{ width: '100%', justifyContent: 'space-between' }}>
              <Space size="small">
                <WarningOutlined style={{
                  color: getAlarmIconColor(device.alarms),
                  fontSize: compact ? 12 : 14
                }} />
                <Text style={{
                  fontSize: compact ? 11 : 12,
                  color: getAlarmIconColor(device.alarms),
                  fontWeight: 500
                }}>
                  {device.alarms.length} allarme{device.alarms.length > 1 ? 'i' : ''} attiv{device.alarms.length > 1 ? 'i' : 'o'}
                </Text>
              </Space>
              {!compact && (
                <Badge
                  count={device.alarms.length}
                  style={{
                    backgroundColor: getAlarmIconColor(device.alarms)
                  }}
                />
              )}
            </Space>
          </div>
        )}
      </div>
    </Card>
  );
}; 