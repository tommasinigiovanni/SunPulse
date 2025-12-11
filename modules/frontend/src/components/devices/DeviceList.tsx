import React, { useState, useMemo } from 'react';
import { 
  Row, 
  Col, 
  Input, 
  Select, 
  Space, 
  Typography, 
  Card, 
  Empty, 
  Spin, 
  Button,
  Statistic,
  Badge
} from 'antd';
import { 
  SearchOutlined, 
  FilterOutlined, 
  AppstoreOutlined, 
  UnorderedListOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { DeviceCard } from './DeviceCard';
import { useDevices } from '@/hooks/useDevices';
import { Device, DeviceType, DeviceStatus, DeviceFilters } from '@/types/device';
import { formatDeviceType, formatDeviceStatus } from '@/utils/formatters';
import { DEVICE_TYPES, DEVICE_STATUS } from '@/utils/constants';

const { Text, Title } = Typography;
const { Option } = Select;

interface DeviceListProps {
  onDeviceClick?: (device: Device) => void;
  selectedDeviceIds?: string[];
  compact?: boolean;
  showFilters?: boolean;
}

export const DeviceList: React.FC<DeviceListProps> = ({
  onDeviceClick,
  selectedDeviceIds = [],
  compact = false,
  showFilters = true,
}) => {
  const [filters, setFilters] = useState<DeviceFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const { 
    devices, 
    isLoading, 
    error, 
    refetch, 
    stats,
    energyStats,
    searchDevices 
  } = useDevices({
    filters,
    pagination: { pageSize: 50 },
  });

  // Filtra dispositivi con ricerca
  const filteredDevices = useMemo(() => {
    if (!searchTerm.trim()) return devices;
    return searchDevices(searchTerm);
  }, [devices, searchTerm, searchDevices]);

  const handleFilterChange = (key: keyof DeviceFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const clearFilters = () => {
    setFilters({});
    setSearchTerm('');
  };

  const getStatusColor = (status: DeviceStatus) => {
    const statusInfo = formatDeviceStatus(status);
    return statusInfo.color;
  };

  if (error) {
    return (
      <Card>
        <Empty
          description="Errore nel caricamento dei dispositivi"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary" onClick={() => refetch()}>
            Riprova
          </Button>
        </Empty>
      </Card>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header con statistiche */}
      <Card size="small">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Statistic
              title="Dispositivi Totali"
              value={stats.total}
              prefix={<AppstoreOutlined />}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Statistic
              title="Online"
              value={stats.online}
              valueStyle={{ color: '#52c41a' }}
              prefix={<Badge status="success" />}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Statistic
              title="Produzione Totale"
              value={`${(energyStats.total_power / 1000).toFixed(1)} kW`}
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Statistic
              title="Energia Oggi"
              value={`${energyStats.daily_energy.toFixed(1)} kWh`}
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
        </Row>
      </Card>

      {/* Filtri e controlli */}
      {showFilters && (
        <Card size="small">
          <Row gutter={[16, 8]} align="middle">
            <Col xs={24} sm={12} md={8}>
              <Input
                placeholder="Cerca dispositivi..."
                prefix={<SearchOutlined />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                allowClear
              />
            </Col>
            
            <Col xs={12} sm={6} md={4}>
              <Select
                placeholder="Tipo"
                value={filters.type}
                onChange={(value) => handleFilterChange('type', value)}
                allowClear
                style={{ width: '100%' }}
              >
                {Object.values(DEVICE_TYPES).map(type => (
                  <Option key={type} value={type}>
                    {formatDeviceType(type)}
                  </Option>
                ))}
              </Select>
            </Col>

            <Col xs={12} sm={6} md={4}>
              <Select
                placeholder="Stato"
                value={filters.status}
                onChange={(value) => handleFilterChange('status', value)}
                allowClear
                style={{ width: '100%' }}
              >
                {Object.values(DEVICE_STATUS).map(status => (
                  <Option key={status} value={status}>
                    <Badge 
                      color={getStatusColor(status)} 
                      text={formatDeviceStatus(status).text} 
                    />
                  </Option>
                ))}
              </Select>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Space>
                <Button
                  icon={<FilterOutlined />}
                  onClick={clearFilters}
                  disabled={Object.keys(filters).length === 0 && !searchTerm}
                >
                  Pulisci Filtri
                </Button>

                <Button
                  icon={<ReloadOutlined />}
                  onClick={() => refetch()}
                  loading={isLoading}
                >
                  Aggiorna
                </Button>

                <Button.Group>
                  <Button
                    icon={<AppstoreOutlined />}
                    type={viewMode === 'grid' ? 'primary' : 'default'}
                    onClick={() => setViewMode('grid')}
                  />
                  <Button
                    icon={<UnorderedListOutlined />}
                    type={viewMode === 'list' ? 'primary' : 'default'}
                    onClick={() => setViewMode('list')}
                  />
                </Button.Group>
              </Space>
            </Col>
          </Row>
        </Card>
      )}

      {/* Lista dispositivi */}
      <div style={{ minHeight: 400 }}>
        {isLoading ? (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: 400 
          }}>
            <Spin size="large" />
          </div>
        ) : filteredDevices.length === 0 ? (
          <Empty
            description={
              searchTerm || Object.keys(filters).length > 0
                ? "Nessun dispositivo trovato con i filtri attuali"
                : "Nessun dispositivo configurato"
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <Row gutter={[16, 16]}>
            {filteredDevices.map(device => (
              <Col 
                key={device.id}
                xs={24}
                sm={viewMode === 'grid' ? 12 : 24}
                md={viewMode === 'grid' ? 8 : 24}
                lg={viewMode === 'grid' ? 6 : 24}
                xl={viewMode === 'grid' ? 4 : 24}
              >
                <DeviceCard
                  device={device}
                  onClick={onDeviceClick}
                  compact={compact || viewMode === 'list'}
                />
              </Col>
            ))}
          </Row>
        )}
      </div>

      {/* Footer con info filtri */}
      {filteredDevices.length > 0 && (
        <div style={{ textAlign: 'center', paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
          <Text type="secondary">
            Visualizzati {filteredDevices.length} di {devices.length} dispositivi
            {(searchTerm || Object.keys(filters).length > 0) && (
              <> • <Button type="link" size="small" onClick={clearFilters}>
                Mostra tutti
              </Button></>
            )}
          </Text>
        </div>
      )}
    </div>
  );
}; 