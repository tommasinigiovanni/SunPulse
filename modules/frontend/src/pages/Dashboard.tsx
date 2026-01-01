import React, { useState, useMemo } from 'react';
import { Row, Col, Card, Statistic, Typography, Space, Divider, Progress, Select, Skeleton, Button, Tooltip } from 'antd';
import {
  ThunderboltOutlined,
  DollarOutlined,
  RiseOutlined,
  FallOutlined,
  CheckCircleOutlined,
  StarOutlined,
  HomeOutlined,
  CloudOutlined,
  BulbOutlined,
  ControlOutlined,
  ReloadOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { PowerChart } from '@/components/charts/PowerChart';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import { useDevices } from '@/hooks/useDevices';
import { useEnergyStats } from '@/hooks/useEnergyStats';
import { formatPower, formatEnergy, formatCurrency, formatCO2 } from '@/utils/formatters';

const { Title, Text } = Typography;

export const Dashboard: React.FC = () => {
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | undefined>(undefined);
  
  const { data: realTimeData, summary, isLoading: realTimeLoading, refreshData, lastUpdate } = useRealTimeData();
  const { devices, stats, energyStats, refetch: refetchDevices } = useDevices();
  const { stats: energyStatsReal, isLoading: energyStatsLoading } = useEnergyStats();

  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await Promise.all([refreshData(), refetchDevices()]);
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const formatLastUpdate = (timestamp: string | undefined) => {
    if (!timestamp) return 'Mai';
    const date = new Date(timestamp);
    const now = new Date();
    const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffSeconds < 60) return `${diffSeconds}s fa`;
    if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)}m fa`;
    return date.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' });
  };
  
  // Opzioni per il selettore dispositivo
  const deviceOptions = useMemo(() => {
    const options = [{ value: 'all', label: '🏠 Tutti i dispositivi' }];
    
    // Aggiungi dispositivi da realTimeData (hanno più info)
    realTimeData?.forEach((device: any) => {
      options.push({
        value: device.device_id || device.thing_key,
        label: `⚡ ${device.name || `Dispositivo ${device.device_id}`}`,
      });
    });
    
    // Fallback a devices se realTimeData è vuoto
    if (realTimeData?.length === 0) {
      devices?.forEach((device) => {
        options.push({
          value: device.id,
          label: `⚡ ${device.name || `Dispositivo ${device.id}`}`,
        });
      });
    }
    
    return options;
  }, [realTimeData, devices]);

  // Calcola metriche dashboard con dati reali
  const dailyEnergy = energyStatsReal.today || summary?.total_energy_today || energyStats.daily_energy || 0;
  const dashboardMetrics = {
    currentPower: summary?.total_power || 0,
    dailyEnergy: dailyEnergy,
    monthlyEnergy: dailyEnergy * 30, // Stima mensile
    yearlyEnergy: dailyEnergy * 365, // Stima annuale
    co2Saved: dailyEnergy * 0.4, // 0.4 kg CO2 per kWh
    moneySaved: dailyEnergy * 0.25, // €0.25 per kWh
    efficiency: energyStatsReal.efficiency, // Efficienza reale calcolata
    variationFromYesterday: energyStatsReal.variationFromYesterday,
    variationFromLastWeek: energyStatsReal.variationFromLastWeek,
  };

  return (
    <div style={{ padding: 24, backgroundColor: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
            Dashboard Fotovoltaico
          </Title>
          <Space>
            <Text type="secondary">
              Monitoraggio in tempo reale del sistema di produzione energia
            </Text>
            <Tooltip title={`Ultimo aggiornamento: ${formatLastUpdate(lastUpdate)}`}>
              <Space size={4} style={{ color: '#999', fontSize: 12 }}>
                <ClockCircleOutlined />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {formatLastUpdate(lastUpdate)}
                </Text>
              </Space>
            </Tooltip>
          </Space>
        </div>

        {/* Controlli */}
        <Space size={8} wrap>
          <Tooltip title="Aggiorna dati">
            <Button
              icon={<ReloadOutlined spin={isRefreshing} />}
              onClick={handleRefresh}
              loading={isRefreshing}
              type="default"
            >
              Aggiorna
            </Button>
          </Tooltip>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <ControlOutlined style={{ color: '#1890ff' }} />
            <Select
              value={selectedDeviceId || 'all'}
              onChange={(value) => setSelectedDeviceId(value === 'all' ? undefined : value)}
              style={{ minWidth: 220 }}
              options={deviceOptions}
              placeholder="Seleziona dispositivo"
            />
          </div>
        </Space>
      </div>

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            {(realTimeLoading || energyStatsLoading) ? (
              <Skeleton active paragraph={{ rows: 1 }} />
            ) : (
              <Statistic
                title="Produzione Attuale"
                value={dashboardMetrics.currentPower}
                formatter={(value) => formatPower(Number(value))}
                prefix={<ThunderboltOutlined style={{ color: '#1890ff' }} />}
                valueStyle={{ color: '#1890ff', fontSize: 28 }}
                suffix={
                  dashboardMetrics.variationFromYesterday !== 0 && (
                    <Space>
                      {dashboardMetrics.variationFromYesterday > 0 ? (
                        <RiseOutlined style={{ color: '#52c41a', fontSize: 14 }} />
                      ) : (
                        <FallOutlined style={{ color: '#ff4d4f', fontSize: 14 }} />
                      )}
                      <Text style={{ fontSize: 12, color: dashboardMetrics.variationFromYesterday > 0 ? '#52c41a' : '#ff4d4f' }}>
                        {dashboardMetrics.variationFromYesterday > 0 ? '+' : ''}{dashboardMetrics.variationFromYesterday.toFixed(1)}%
                      </Text>
                    </Space>
                  )
                }
              />
            )}
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            {(realTimeLoading || energyStatsLoading) ? (
              <Skeleton active paragraph={{ rows: 1 }} />
            ) : (
              <Statistic
                title="Energia Prodotta Oggi"
                value={dashboardMetrics.dailyEnergy}
                formatter={(value) => formatEnergy(Number(value) * 1000)}
                prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                valueStyle={{ color: '#52c41a', fontSize: 28 }}
                suffix={
                  dashboardMetrics.variationFromYesterday !== 0 && (
                    <Space>
                      {dashboardMetrics.variationFromYesterday > 0 ? (
                        <RiseOutlined style={{ color: '#52c41a', fontSize: 14 }} />
                      ) : (
                        <FallOutlined style={{ color: '#ff4d4f', fontSize: 14 }} />
                      )}
                      <Text style={{ fontSize: 12, color: dashboardMetrics.variationFromYesterday > 0 ? '#52c41a' : '#ff4d4f' }}>
                        {dashboardMetrics.variationFromYesterday > 0 ? '+' : ''}{dashboardMetrics.variationFromYesterday.toFixed(1)}%
                      </Text>
                    </Space>
                  )
                }
              />
            )}
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            {(realTimeLoading || energyStatsLoading) ? (
              <Skeleton active paragraph={{ rows: 1 }} />
            ) : (
              <Statistic
              title="Risparmio Oggi"
              value={dashboardMetrics.moneySaved}
              formatter={(value) => formatCurrency(Number(value))}
              prefix={<DollarOutlined style={{ color: '#faad14' }} />}
              valueStyle={{ color: '#faad14', fontSize: 28 }}
              suffix={
                dashboardMetrics.variationFromYesterday !== 0 && (
                  <Space>
                    {dashboardMetrics.variationFromYesterday > 0 ? (
                      <RiseOutlined style={{ color: '#52c41a', fontSize: 14 }} />
                    ) : (
                      <FallOutlined style={{ color: '#ff4d4f', fontSize: 14 }} />
                    )}
                    <Text style={{ fontSize: 12, color: dashboardMetrics.variationFromYesterday > 0 ? '#52c41a' : '#ff4d4f' }}>
                      {dashboardMetrics.variationFromYesterday > 0 ? '+' : ''}{dashboardMetrics.variationFromYesterday.toFixed(1)}%
                    </Text>
                  </Space>
                )
              }
              />
            )}
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            {(realTimeLoading || energyStatsLoading) ? (
              <Skeleton active paragraph={{ rows: 1 }} />
            ) : (
              <Statistic
              title="CO₂ Risparmiata"
              value={dashboardMetrics.co2Saved}
              formatter={(value) => formatCO2(Number(value))}
              prefix={<StarOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a', fontSize: 28 }}
              suffix={
                dashboardMetrics.variationFromYesterday !== 0 && (
                  <Space>
                    {dashboardMetrics.variationFromYesterday > 0 ? (
                      <RiseOutlined style={{ color: '#52c41a', fontSize: 14 }} />
                    ) : (
                      <FallOutlined style={{ color: '#ff4d4f', fontSize: 14 }} />
                    )}
                    <Text style={{ fontSize: 12, color: dashboardMetrics.variationFromYesterday > 0 ? '#52c41a' : '#ff4d4f' }}>
                      {dashboardMetrics.variationFromYesterday > 0 ? '+' : ''}{dashboardMetrics.variationFromYesterday.toFixed(1)}%
                    </Text>
                  </Space>
                )
              }
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* Bilancio Energetico Giornaliero */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {/* Consumo Giornaliero */}
        <Col xs={24} lg={8}>
          <Card 
            size="small" 
            title={
              <Space>
                <BulbOutlined style={{ color: '#faad14' }} />
                <span>Consumo Giornaliero</span>
              </Space>
            }
          >
            <div style={{ textAlign: 'center', marginBottom: 12 }}>
              <Text style={{ fontSize: 28, fontWeight: 'bold', color: '#faad14' }}>
                {(summary?.energy_consumed_today || 0).toFixed(2)} kWh
              </Text>
            </div>
            <Space direction="vertical" style={{ width: '100%' }} size={8}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: '#f6ffed', borderRadius: 4 }}>
                <Text>☀️ Dal Sole (autoconsumo)</Text>
                <Text strong style={{ color: '#52c41a' }}>
                  {(summary?.energy_self_consumed_today || 0).toFixed(2)} kWh
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: '#e6f7ff', borderRadius: 4 }}>
                <Text>🔌 Dalla Rete</Text>
                <Text strong style={{ color: '#1890ff' }}>
                  {(summary?.energy_from_grid_today || 0).toFixed(2)} kWh
                </Text>
              </div>
              {(summary?.energy_from_battery_today || 0) > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: '#f9f0ff', borderRadius: 4 }}>
                  <Text>🔋 Dalla Batteria</Text>
                  <Text strong style={{ color: '#722ed1' }}>
                    {(summary?.energy_from_battery_today || 0).toFixed(2)} kWh
                  </Text>
                </div>
              )}
            </Space>
          </Card>
        </Col>
        
        {/* Produzione Giornaliera */}
        <Col xs={24} lg={8}>
          <Card 
            size="small"
            title={
              <Space>
                <ThunderboltOutlined style={{ color: '#52c41a' }} />
                <span>Produzione Giornaliera</span>
              </Space>
            }
          >
            <div style={{ textAlign: 'center', marginBottom: 12 }}>
              <Text style={{ fontSize: 28, fontWeight: 'bold', color: '#52c41a' }}>
                {(summary?.total_energy_today || 0).toFixed(2)} kWh
              </Text>
            </div>
            <Space direction="vertical" style={{ width: '100%' }} size={8}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: '#f6ffed', borderRadius: 4 }}>
                <Text>🏠 Autoconsumo</Text>
                <Text strong style={{ color: '#52c41a' }}>
                  {(summary?.energy_self_consumed_today || 0).toFixed(2)} kWh
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: '#e6f7ff', borderRadius: 4 }}>
                <Text>⚡ Immesso in Rete</Text>
                <Text strong style={{ color: '#1890ff' }}>
                  {(summary?.energy_to_grid_today || 0).toFixed(2)} kWh
                </Text>
              </div>
              {(summary?.energy_to_battery_today || 0) > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: '#f9f0ff', borderRadius: 4 }}>
                  <Text>🔋 Verso Batteria</Text>
                  <Text strong style={{ color: '#722ed1' }}>
                    {(summary?.energy_to_battery_today || 0).toFixed(2)} kWh
                  </Text>
                </div>
              )}
            </Space>
          </Card>
        </Col>
        
        {/* Stato Istantaneo */}
        <Col xs={24} lg={8}>
          <Card 
            size="small"
            title={
              <Space>
                <CloudOutlined style={{ color: '#1890ff' }} />
                <span>Potenza Istantanea</span>
              </Space>
            }
          >
            <Row gutter={[8, 16]}>
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 11 }}>Produzione</Text>
                  <div style={{ fontSize: 18, fontWeight: 'bold', color: '#52c41a' }}>
                    {((summary?.total_power || 0) / 1000).toFixed(2)} kW
                  </div>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 11 }}>Consumo</Text>
                  <div style={{ fontSize: 18, fontWeight: 'bold', color: '#faad14' }}>
                    {((summary?.total_power_consuming || 0) / 1000).toFixed(2)} kW
                  </div>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 11 }}>Dalla Rete</Text>
                  <div style={{ fontSize: 16, fontWeight: 'bold', color: '#1890ff' }}>
                    {((summary?.from_grid || 0) / 1000).toFixed(2)} kW
                  </div>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 11 }}>In Rete</Text>
                  <div style={{ fontSize: 16, fontWeight: 'bold', color: '#52c41a' }}>
                    {((summary?.to_grid || 0) / 1000).toFixed(2)} kW
                  </div>
                </div>
              </Col>
            </Row>
            {(summary?.battery_soc ?? 0) > 0 && (
              <>
                <Divider style={{ margin: '8px 0' }} />
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text>🔋 Batteria</Text>
                  <Progress 
                    percent={summary?.battery_soc || 0} 
                    size="small" 
                    style={{ width: 100 }}
                    strokeColor={summary?.battery_soc > 50 ? '#52c41a' : summary?.battery_soc > 20 ? '#faad14' : '#ff4d4f'}
                  />
                </div>
              </>
            )}
          </Card>
        </Col>
      </Row>

      {/* Grafico Principale - Full width */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <PowerChart 
            height={400}
            title={selectedDeviceId ? `Produzione vs Consumo - ${deviceOptions.find(d => d.value === selectedDeviceId)?.label || 'Dispositivo'}` : "Produzione vs Consumo - Tutti i dispositivi"}
            deviceIds={selectedDeviceId ? [selectedDeviceId] : undefined}
            autoRefresh={true}
          />
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