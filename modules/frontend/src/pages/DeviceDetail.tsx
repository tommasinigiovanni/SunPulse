import React, { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  Typography, 
  Space, 
  Button, 
  Descriptions,
  Badge,
  Spin,
  Empty,
  Divider,
  Progress
} from 'antd';
import { 
  ArrowLeftOutlined,
  ThunderboltOutlined, 
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  ToolOutlined,
  SyncOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { PowerChart } from '@/components/charts/PowerChart';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import { formatPower, formatEnergy, formatDeviceStatus, formatRelativeTime } from '@/utils/formatters';

const { Title, Text } = Typography;

export const DeviceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  // Carica dati del dispositivo specifico
  const { data: realTimeData, summary, isLoading, refreshData } = useRealTimeData({
    deviceIds: id ? [id] : undefined,
  });

  // Trova il dispositivo nei dati
  const device = useMemo(() => {
    if (!realTimeData || realTimeData.length === 0) return null;
    return realTimeData.find((d: any) => 
      d.device_id === id || d.thing_key === id
    ) || realTimeData[0];
  }, [realTimeData, id]);

  // Estrai dati ZCS raw se disponibili
  const zcsData = useMemo(() => {
    if (!device?.raw_data?.realtimeData?.params?.value?.[0]) return null;
    const thingKey = device.thing_key || Object.keys(device.raw_data.realtimeData.params.value[0])[0];
    return device.raw_data.realtimeData.params.value[0][thingKey] || null;
  }, [device]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 24 }} />;
      case 'offline':
        return <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 24 }} />;
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14', fontSize: 24 }} />;
      case 'maintenance':
        return <ToolOutlined style={{ color: '#1890ff', fontSize: 24 }} />;
      default:
        return <CloseCircleOutlined style={{ color: '#d9d9d9', fontSize: 24 }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return '#52c41a';
      case 'offline': return '#ff4d4f';
      case 'warning': return '#faad14';
      case 'maintenance': return '#1890ff';
      default: return '#d9d9d9';
    }
  };

  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: 400 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!device) {
    return (
      <div style={{ padding: 24 }}>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate('/devices')}
          style={{ marginBottom: 16 }}
        >
          Torna ai dispositivi
        </Button>
        <Empty description={`Dispositivo ${id} non trovato`} />
      </div>
    );
  }

  const statusInfo = formatDeviceStatus(device.status || 'online');

  return (
    <div style={{ padding: 24, backgroundColor: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate('/devices')}
          style={{ marginBottom: 16 }}
        >
          Torna ai dispositivi
        </Button>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <Space align="center" size={16}>
              {getStatusIcon(device.status || 'online')}
              <div>
                <Title level={2} style={{ margin: 0 }}>
                  {device.name || `Dispositivo ${device.device_id}`}
                </Title>
                <Space>
                  <Badge color={getStatusColor(device.status || 'online')} text={statusInfo.text} />
                  <Text type="secondary">•</Text>
                  <Text type="secondary">{device.thing_key || device.serial_number}</Text>
                </Space>
              </div>
            </Space>
          </div>
          
          <Space>
            <Button 
              icon={<SyncOutlined />} 
              onClick={refreshData}
            >
              Aggiorna
            </Button>
            <Button 
              icon={<SettingOutlined />}
              disabled
            >
              Configura
            </Button>
          </Space>
        </div>
      </div>

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Potenza Attuale"
              value={device.power || zcsData?.powerGenerating || 0}
              formatter={(value) => formatPower(Number(value))}
              prefix={<ThunderboltOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff', fontSize: 24 }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Energia Prodotta Oggi"
              value={device.energy_today || zcsData?.energyGenerating || 0}
              formatter={(value) => `${Number(value).toFixed(2)} kWh`}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a', fontSize: 24 }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Consumo"
              value={zcsData?.powerConsuming || 0}
              formatter={(value) => formatPower(Number(value))}
              valueStyle={{ color: '#faad14', fontSize: 24 }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Stato Batteria"
              value={device.battery_soc || zcsData?.batterySoC || 0}
              suffix="%"
              valueStyle={{ 
                color: (device.battery_soc || zcsData?.batterySoC || 0) > 50 ? '#52c41a' : 
                       (device.battery_soc || zcsData?.batterySoC || 0) > 20 ? '#faad14' : '#ff4d4f',
                fontSize: 24 
              }}
            />
            {(device.battery_soc || zcsData?.batterySoC) > 0 && (
              <Progress 
                percent={device.battery_soc || zcsData?.batterySoC || 0} 
                showInfo={false}
                strokeColor={
                  (device.battery_soc || zcsData?.batterySoC || 0) > 50 ? '#52c41a' : 
                  (device.battery_soc || zcsData?.batterySoC || 0) > 20 ? '#faad14' : '#ff4d4f'
                }
                size="small"
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* Bilancio Energetico Giornaliero */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={12}>
          <Card title="🔋 Produzione Oggi" size="small">
            <Space direction="vertical" style={{ width: '100%' }} size={8}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#f6ffed', borderRadius: 4 }}>
                <Text>☀️ Energia Generata</Text>
                <Text strong style={{ color: '#52c41a' }}>
                  {(zcsData?.energyGenerating || device.energy_today || 0).toFixed(2)} kWh
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#e6f7ff', borderRadius: 4 }}>
                <Text>⚡ Immesso in Rete</Text>
                <Text strong style={{ color: '#1890ff' }}>
                  {(zcsData?.energyExporting || 0).toFixed(2)} kWh
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#f9f0ff', borderRadius: 4 }}>
                <Text>🔋 Caricato in Batteria</Text>
                <Text strong style={{ color: '#722ed1' }}>
                  {(zcsData?.energyCharging || 0).toFixed(2)} kWh
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#fffbe6', borderRadius: 4 }}>
                <Text>🏠 Autoconsumo</Text>
                <Text strong style={{ color: '#faad14' }}>
                  {(zcsData?.energyAutoconsuming || 0).toFixed(2)} kWh
                </Text>
              </div>
            </Space>
          </Card>
        </Col>
        
        <Col xs={24} md={12}>
          <Card title="🏠 Consumo Oggi" size="small">
            <Space direction="vertical" style={{ width: '100%' }} size={8}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#fff2e8', borderRadius: 4 }}>
                <Text>⚡ Consumo Totale</Text>
                <Text strong style={{ color: '#fa8c16' }}>
                  {(zcsData?.energyConsuming || 0).toFixed(2)} kWh
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#f6ffed', borderRadius: 4 }}>
                <Text>☀️ Dal Sole</Text>
                <Text strong style={{ color: '#52c41a' }}>
                  {(zcsData?.energyAutoconsuming || 0).toFixed(2)} kWh
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#f9f0ff', borderRadius: 4 }}>
                <Text>🔋 Dalla Batteria</Text>
                <Text strong style={{ color: '#722ed1' }}>
                  {(zcsData?.energyDischarging || 0).toFixed(2)} kWh
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#e6f7ff', borderRadius: 4 }}>
                <Text>🔌 Dalla Rete</Text>
                <Text strong style={{ color: '#1890ff' }}>
                  {(zcsData?.energyImporting || 0).toFixed(2)} kWh
                </Text>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Grafico */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <PowerChart 
            height={350}
            title={`Produzione vs Consumo - ${device.name || 'Dispositivo'}`}
            deviceIds={id ? [id] : undefined}
            autoRefresh={false}
          />
        </Col>
      </Row>

      {/* Dettagli Tecnici */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="📊 Dati Real-Time" size="small">
            <Descriptions column={2} size="small">
              <Descriptions.Item label="Potenza Generazione">
                {formatPower(zcsData?.powerGenerating || 0)}
              </Descriptions.Item>
              <Descriptions.Item label="Potenza Consumo">
                {formatPower(zcsData?.powerConsuming || 0)}
              </Descriptions.Item>
              <Descriptions.Item label="Potenza Importazione">
                {formatPower(zcsData?.powerImporting || 0)}
              </Descriptions.Item>
              <Descriptions.Item label="Potenza Esportazione">
                {formatPower(zcsData?.powerExporting || 0)}
              </Descriptions.Item>
              <Descriptions.Item label="Potenza Carica Batteria">
                {formatPower(zcsData?.powerCharging || 0)}
              </Descriptions.Item>
              <Descriptions.Item label="Potenza Scarica Batteria">
                {formatPower(zcsData?.powerDischarging || 0)}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card title="📈 Totali Storici" size="small">
            <Descriptions column={2} size="small">
              <Descriptions.Item label="Energia Generata Totale">
                {((zcsData?.energyGeneratingTotal || 0) / 1000).toFixed(1)} MWh
              </Descriptions.Item>
              <Descriptions.Item label="Energia Consumata Totale">
                {((zcsData?.energyConsumingTotal || 0) / 1000).toFixed(1)} MWh
              </Descriptions.Item>
              <Descriptions.Item label="Energia Importata Totale">
                {((zcsData?.energyImportingTotal || 0) / 1000).toFixed(1)} MWh
              </Descriptions.Item>
              <Descriptions.Item label="Energia Esportata Totale">
                {((zcsData?.energyExportingTotal || 0) / 1000).toFixed(1)} MWh
              </Descriptions.Item>
              <Descriptions.Item label="Cicli Batteria">
                {zcsData?.batteryCycletime || 0}
              </Descriptions.Item>
              <Descriptions.Item label="Ultimo Aggiornamento">
                {device.last_update ? formatRelativeTime(device.last_update) : 'N/A'}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>
    </div>
  );
};
