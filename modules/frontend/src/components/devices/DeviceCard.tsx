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

  const cardTitle = (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Space>
        <Text strong style={{ fontSize: compact ? 14 : 16 }}>
          {device.name}
        </Text>
        <Badge 
          color={statusInfo.color} 
          text={
            <Text style={{ fontSize: 12, color: statusInfo.color }}>
              {statusInfo.text}
            </Text>
          } 
        />
      </Space>
      {getStatusIcon()}
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
            formatter={(value) => formatEnergy(Number(value) * 1000)} // Convert kWh to Wh for formatting
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

        {/* Alarms - Temporarily disabled */}
        {/* {device.alarms && device.alarms.length > 0 && (
          <div style={{ 
            marginTop: compact ? 4 : 8,
            padding: compact ? 4 : 8,
            background: '#fff2e8',
            borderRadius: 4,
            border: '1px solid #ffbb96'
          }}>
            <Space size="small">
              <WarningOutlined style={{ color: '#fa8c16', fontSize: compact ? 12 : 14 }} />
              <Text style={{ fontSize: compact ? 11 : 12, color: '#fa8c16' }}>
                {device.alarms.length} allarme{device.alarms.length > 1 ? 'i' : ''} attiv{device.alarms.length > 1 ? 'i' : 'o'}
              </Text>
            </Space>
          </div>
        )} */}
      </div>
    </Card>
  );
}; 