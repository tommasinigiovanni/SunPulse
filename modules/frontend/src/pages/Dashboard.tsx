import React from 'react';
import { Row, Col, Card, Statistic, Typography, Space, Divider } from 'antd';
import { 
  ThunderboltOutlined, 
  DollarOutlined, 
  RiseOutlined,
  FallOutlined,
  CheckCircleOutlined,
  StarOutlined
} from '@ant-design/icons';
import { PowerChart } from '@/components/charts/PowerChart';
import { DeviceList } from '@/components/devices/DeviceList';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import { useDevices } from '@/hooks/useDevices';
import { formatPower, formatEnergy, formatCurrency, formatCO2 } from '@/utils/formatters';

const { Title, Text } = Typography;

export const Dashboard: React.FC = () => {
  const { data: realTimeData, summary, isLoading: realTimeLoading } = useRealTimeData();
  const { devices, stats, energyStats } = useDevices();

  // Calcola metriche dashboard
  const dashboardMetrics = {
    currentPower: summary?.total_power || 0,
    dailyEnergy: summary?.total_energy_today || 0,
    monthlyEnergy: energyStats.daily_energy * 30, // Stima mensile
    yearlyEnergy: energyStats.daily_energy * 365, // Stima annuale
    co2Saved: (summary?.total_energy_today || 0) * 0.4, // 0.4 kg CO2 per kWh
    moneySaved: (summary?.total_energy_today || 0) * 0.25, // €0.25 per kWh
    efficiency: 85.5, // Valore di esempio
  };

  return (
    <div style={{ padding: 24, backgroundColor: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
          Dashboard Fotovoltaico
        </Title>
        <Text type="secondary">
          Monitoraggio in tempo reale del sistema di produzione energia
        </Text>
      </div>

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Produzione Attuale"
              value={dashboardMetrics.currentPower}
              formatter={(value) => formatPower(Number(value))}
              prefix={<ThunderboltOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff', fontSize: 28 }}
              suffix={
                <Space>
                  <RiseOutlined style={{ color: '#52c41a', fontSize: 14 }} />
                  <Text style={{ fontSize: 12, color: '#52c41a' }}>+5.2%</Text>
                </Space>
              }
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Energia Oggi"
              value={dashboardMetrics.dailyEnergy}
              formatter={(value) => formatEnergy(Number(value) * 1000)}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a', fontSize: 28 }}
              suffix={
                <Space>
                  <RiseOutlined style={{ color: '#52c41a', fontSize: 14 }} />
                  <Text style={{ fontSize: 12, color: '#52c41a' }}>+12%</Text>
                </Space>
              }
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Risparmio Oggi"
              value={dashboardMetrics.moneySaved}
              formatter={(value) => formatCurrency(Number(value))}
              prefix={<DollarOutlined style={{ color: '#faad14' }} />}
              valueStyle={{ color: '#faad14', fontSize: 28 }}
              suffix={
                <Space>
                  <RiseOutlined style={{ color: '#52c41a', fontSize: 14 }} />
                  <Text style={{ fontSize: 12, color: '#52c41a' }}>+8%</Text>
                </Space>
              }
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="CO₂ Risparmiata"
              value={dashboardMetrics.co2Saved}
              formatter={(value) => formatCO2(Number(value))}
              prefix={<StarOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a', fontSize: 28 }}
              suffix={
                <Space>
                  <RiseOutlined style={{ color: '#52c41a', fontSize: 14 }} />
                  <Text style={{ fontSize: 12, color: '#52c41a' }}>+15%</Text>
                </Space>
              }
            />
          </Card>
        </Col>
      </Row>

      {/* Seconda riga di metriche */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Dispositivi Online"
              value={`${stats.online}/${stats.total}`}
              valueStyle={{ 
                color: stats.online === stats.total ? '#52c41a' : '#faad14',
                fontSize: 20 
              }}
              suffix={
                <Text style={{ fontSize: 14, color: '#666' }}>
                  ({((stats.online / stats.total) * 100).toFixed(0)}%)
                </Text>
              }
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Efficienza Sistema"
              value={dashboardMetrics.efficiency}
              suffix="%"
              valueStyle={{ 
                color: dashboardMetrics.efficiency > 80 ? '#52c41a' : '#faad14',
                fontSize: 20 
              }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Energia Mensile"
              value={dashboardMetrics.monthlyEnergy}
              formatter={(value) => formatEnergy(Number(value) * 1000)}
              valueStyle={{ color: '#1890ff', fontSize: 20 }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Grafico Principale */}
        <Col xs={24} lg={16}>
          <PowerChart 
            height={400}
            title="Produzione vs Consumo - Ultime 24 ore"
            autoRefresh={true}
          />
        </Col>
        
        {/* Pannello Dispositivi */}
        <Col xs={24} lg={8}>
          <Card 
            title="Stato Dispositivi" 
            size="small"
            style={{ height: 460 }}
            bodyStyle={{ 
              padding: 12,
              height: 'calc(100% - 57px)',
              overflow: 'auto'
            }}
          >
            <DeviceList 
              compact={true}
              showFilters={false}
            />
          </Card>
        </Col>
      </Row>

      {/* Sezione Analytics estesa */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="Analytics Avanzate" size="small">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
                    {formatEnergy(dashboardMetrics.yearlyEnergy * 1000)}
                  </div>
                  <Text type="secondary">Produzione Annuale Stimata</Text>
                </div>
              </Col>
              
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>
                    {formatCurrency(dashboardMetrics.moneySaved * 365)}
                  </div>
                  <Text type="secondary">Risparmio Annuale Stimato</Text>
                </div>
              </Col>
              
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>
                    {formatCO2(dashboardMetrics.co2Saved * 365)}
                  </div>
                  <Text type="secondary">CO₂ Risparmiata Annuale</Text>
                </div>
              </Col>
              
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
                    {Math.round(dashboardMetrics.co2Saved * 365 / 20)}
                  </div>
                  <Text type="secondary">Alberi Equivalenti</Text>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
}; 