import React, { useState, useMemo, useEffect } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  Typography, 
  Space, 
  Select,
  DatePicker,
  Segmented,
  Table,
  Progress,
  Skeleton,
  Spin
} from 'antd';
import { 
  ThunderboltOutlined, 
  RiseOutlined,
  FallOutlined,
  BarChartOutlined,
  CalendarOutlined,
  DollarOutlined,
  CloudOutlined
} from '@ant-design/icons';
import { Column, Pie } from '@ant-design/charts';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import { apiClient } from '@/utils/api';
import { formatEnergy, formatCurrency, formatCO2 } from '@/utils/formatters';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

type PeriodType = 'today' | 'week' | 'month' | 'year';

export const Analytics: React.FC = () => {
  const [period, setPeriod] = useState<PeriodType>('month');
  const [viewType, setViewType] = useState<'energy' | 'money' | 'co2'>('energy');
  
  // Stato per dati storici reali (deve essere prima di metrics che lo usa)
  const [historicalDailyData, setHistoricalDailyData] = useState<any[]>([]);
  const [historicalLoading, setHistoricalLoading] = useState(true); // Start with loading=true
  
  const { summary } = useRealTimeData();

  // Carica dati storici giornalieri dal backend
  useEffect(() => {
    const fetchDailyEnergy = async () => {
      try {
        setHistoricalLoading(true);
        const days = period === 'today' ? 1 : period === 'week' ? 7 : period === 'month' ? 30 : 365;
        
        const response = await apiClient.getDailyEnergyHistory(days);
        
        if (response?.data && response.data.length > 0) {
          setHistoricalDailyData(response.data);
        }
      } catch (err) {
        console.warn('Dati energia giornaliera non disponibili:', err);
      } finally {
        setHistoricalLoading(false);
      }
    };
    
    fetchDailyEnergy();
  }, [period]);

  // Calcola metriche aggregate dai dati storici reali
  const metrics = useMemo(() => {
    // Se abbiamo dati storici, usa quelli per calcolare i totali
    if (historicalDailyData.length > 0) {
      const production = historicalDailyData.reduce((sum, day) => sum + (day.production_kwh || 0), 0);
      const consumption = historicalDailyData.reduce((sum, day) => sum + (day.consumption_kwh || 0), 0);
      
      // Stima autoconsumo come min(produzione, consumo) per ogni giorno
      // In realtà dovrebbe venire dal backend, ma per ora usiamo questa approssimazione
      const selfConsumption = historicalDailyData.reduce((sum, day) => {
        return sum + Math.min(day.production_kwh || 0, day.consumption_kwh || 0);
      }, 0);
      
      // Stima dalla rete = consumo - autoconsumo
      const fromGrid = Math.max(0, consumption - selfConsumption);
      
      // Stima verso rete = produzione - autoconsumo
      const toGrid = Math.max(0, production - selfConsumption);
      
      // Per ora non abbiamo dati storici batteria, usa 0
      const fromBattery = 0;
      const toBattery = 0;
      
      // Calcolo tasso autoconsumo: quanto della produzione viene usata direttamente
      const selfConsumptionRate = production > 0 
        ? (selfConsumption / production) * 100 
        : 0;
      
      // Calcolo tasso autosufficienza: quanto del consumo viene coperto da fonti proprie
      const autarkyRate = consumption > 0 
        ? (selfConsumption / consumption) * 100 
        : 0;
      
      return {
        production,
        consumption,
        selfConsumption,
        fromGrid,
        toGrid,
        fromBattery,
        toBattery,
        selfConsumptionRate: Math.min(100, selfConsumptionRate),
        autarkyRate: Math.min(100, autarkyRate),
        co2Saved: production * 0.4, // kg CO2 per kWh
        moneySaved: selfConsumption * 0.25, // €/kWh autoconsumo
        moneyEarned: toGrid * 0.10, // €/kWh venduto
      };
    }
    
    // Fallback: usa dati di oggi (solo per "Oggi")
    const dailyProduction = summary?.total_energy_today || 0;
    const dailyConsumption = summary?.energy_consumed_today || 0;
    const dailySelfConsumption = summary?.energy_self_consumed_today || 0;
    const dailyFromGrid = summary?.energy_from_grid_today || 0;
    const dailyToGrid = summary?.energy_to_grid_today || 0;
    const dailyFromBattery = summary?.energy_from_battery_today || 0;
    const dailyToBattery = summary?.energy_to_battery_today || 0;
    
    const selfConsumptionRate = dailyProduction > 0 
      ? (dailySelfConsumption / dailyProduction) * 100 
      : 0;
    
    const autarkyRate = dailyConsumption > 0 
      ? ((dailySelfConsumption + dailyFromBattery) / dailyConsumption) * 100 
      : 0;
    
    return {
      production: dailyProduction,
      consumption: dailyConsumption,
      selfConsumption: dailySelfConsumption,
      fromGrid: dailyFromGrid,
      toGrid: dailyToGrid,
      fromBattery: dailyFromBattery,
      toBattery: dailyToBattery,
      selfConsumptionRate: Math.min(100, selfConsumptionRate),
      autarkyRate: Math.min(100, autarkyRate),
      co2Saved: dailyProduction * 0.4,
      moneySaved: dailySelfConsumption * 0.25,
      moneyEarned: dailyToGrid * 0.10,
    };
  }, [summary, period, historicalDailyData]);

  // Dati per grafico a barre (produzione vs consumo per giorno)
  const barChartData = useMemo(() => {
    const days = period === 'today' ? 1 : period === 'week' ? 7 : period === 'month' ? 30 : 12;
    const data = [];
    
    // Se abbiamo dati storici reali dal nuovo endpoint, usali
    if (historicalDailyData.length > 0) {
      const recentData = historicalDailyData.slice(-days);
      
      for (const point of recentData) {
        data.push({
          date: point.date_label,
          value: point.production_kwh || 0,
          type: 'Produzione',
        });
        data.push({
          date: point.date_label,
          value: point.consumption_kwh || 0,
          type: 'Consumo',
        });
      }
      
      return data;
    }
    
    // Fallback: genera dati stimati basati su oggi
    const dailyProduction = summary?.total_energy_today || 0;
    const dailyConsumption = summary?.energy_consumed_today || 0;
    
    for (let i = days - 1; i >= 0; i--) {
      const date = dayjs().subtract(i, period === 'year' ? 'month' : 'day');
      const label = period === 'year' ? date.format('MMM') : date.format('DD/MM');
      
      // Per oggi usa dati reali, per altri giorni stima basata su media
      const isToday = i === 0;
      const avgProduction = isToday ? dailyProduction : dailyProduction * 0.9;
      const avgConsumption = isToday ? dailyConsumption : dailyConsumption * 0.95;
      
      data.push({
        date: label,
        value: avgProduction,
        type: 'Produzione',
      });
      data.push({
        date: label,
        value: avgConsumption,
        type: 'Consumo',
      });
    }
    
    return data;
  }, [summary, period, historicalDailyData]);

  // Dati per grafico a torta (distribuzione consumo)
  const pieChartData = useMemo(() => [
    { type: 'Dal Sole', value: metrics.selfConsumption, color: '#52c41a' },
    { type: 'Dalla Batteria', value: metrics.fromBattery, color: '#722ed1' },
    { type: 'Dalla Rete', value: metrics.fromGrid, color: '#1890ff' },
  ], [metrics]);

  // Dati per grafico a torta (distribuzione produzione)
  const productionPieData = useMemo(() => [
    { type: 'Autoconsumo', value: metrics.selfConsumption, color: '#52c41a' },
    { type: 'Verso Batteria', value: metrics.toBattery, color: '#722ed1' },
    { type: 'Verso Rete', value: metrics.toGrid, color: '#1890ff' },
  ], [metrics]);

  const barConfig = {
    data: barChartData,
    isGroup: true,
    xField: 'date',
    yField: 'value',
    seriesField: 'type',
    color: ['#52c41a', '#faad14'],
    columnStyle: { radius: [4, 4, 0, 0] },
    legend: { position: 'top' as const },
    yAxis: {
      label: {
        formatter: (v: string) => `${Number(v).toFixed(0)} kWh`,
      },
    },
    tooltip: {
      formatter: (datum: any) => ({
        name: datum.type,
        value: `${Number(datum.value).toFixed(2)} kWh`,
      }),
    },
  };

  const pieConfig = {
    data: pieChartData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    innerRadius: 0.6,
    color: ['#52c41a', '#722ed1', '#1890ff'],
    label: {
      type: 'outer',
      content: '{name}: {percentage}',
    },
    legend: { position: 'bottom' as const },
    statistic: {
      title: {
        content: 'Consumo',
        style: { fontSize: '14px' },
      },
      content: {
        content: `${metrics.consumption.toFixed(0)} kWh`,
        style: { fontSize: '20px' },
      },
    },
  };

  const getPeriodLabel = () => {
    switch (period) {
      case 'today': return 'Oggi';
      case 'week': return 'Questa Settimana';
      case 'month': return 'Questo Mese';
      case 'year': return 'Quest\'Anno';
    }
  };

  return (
    <div style={{ padding: 24, backgroundColor: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
            <BarChartOutlined /> Analytics
          </Title>
          <Text type="secondary">
            Analisi dettagliata della produzione e consumo energetico
          </Text>
        </div>
        
        <Space wrap>
          <Segmented
            value={period}
            onChange={(value) => setPeriod(value as PeriodType)}
            options={[
              { label: 'Oggi', value: 'today' },
              { label: 'Settimana', value: 'week' },
              { label: 'Mese', value: 'month' },
              { label: 'Anno', value: 'year' },
            ]}
          />
        </Space>
      </div>

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Skeleton loading={historicalLoading && period !== 'today'} active paragraph={false}>
              <Statistic
                title={`Produzione ${getPeriodLabel()}`}
                value={metrics.production}
                precision={1}
                suffix="kWh"
                prefix={<ThunderboltOutlined style={{ color: '#52c41a' }} />}
                valueStyle={{ color: '#52c41a', fontSize: 24 }}
              />
            </Skeleton>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Skeleton loading={historicalLoading && period !== 'today'} active paragraph={false}>
              <Statistic
                title={`Consumo ${getPeriodLabel()}`}
                value={metrics.consumption}
                precision={1}
                suffix="kWh"
                prefix={<FallOutlined style={{ color: '#faad14' }} />}
                valueStyle={{ color: '#faad14', fontSize: 24 }}
              />
            </Skeleton>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Skeleton loading={historicalLoading && period !== 'today'} active paragraph={false}>
              <Statistic
                title="Risparmio"
                value={metrics.moneySaved + metrics.moneyEarned}
                precision={2}
                prefix={<DollarOutlined style={{ color: '#52c41a' }} />}
                suffix="€"
                valueStyle={{ color: '#52c41a', fontSize: 24 }}
              />
              <Text type="secondary" style={{ fontSize: 11 }}>
                Autoconsumo: €{metrics.moneySaved.toFixed(2)} | Vendita: €{metrics.moneyEarned.toFixed(2)}
              </Text>
            </Skeleton>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Skeleton loading={historicalLoading && period !== 'today'} active paragraph={false}>
              <Statistic
                title="CO₂ Risparmiata"
                value={metrics.co2Saved}
                precision={1}
                suffix="kg"
                prefix={<CloudOutlined style={{ color: '#52c41a' }} />}
                valueStyle={{ color: '#52c41a', fontSize: 24 }}
              />
            </Skeleton>
          </Card>
        </Col>
      </Row>

      {/* Indicatori di performance */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={12}>
          <Card title="📊 Tasso di Autoconsumo" size="small">
            <div style={{ padding: '8px 0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <Text>Percentuale energia prodotta usata direttamente</Text>
                <Text strong style={{ color: '#52c41a' }}>{metrics.selfConsumptionRate.toFixed(0)}%</Text>
              </div>
              <Progress 
                percent={Math.min(100, metrics.selfConsumptionRate)} 
                strokeColor="#52c41a"
                showInfo={false}
              />
            </div>
          </Card>
        </Col>
        
        <Col xs={24} md={12}>
          <Card title="🏠 Tasso di Autosufficienza" size="small">
            <div style={{ padding: '8px 0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <Text>Percentuale consumo coperta da produzione propria</Text>
                <Text strong style={{ color: '#1890ff' }}>{metrics.autarkyRate.toFixed(0)}%</Text>
              </div>
              <Progress 
                percent={Math.min(100, metrics.autarkyRate)} 
                strokeColor="#1890ff"
                showInfo={false}
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* Grafici */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title={`📈 Produzione vs Consumo - ${getPeriodLabel()}`}>
            <Spin spinning={historicalLoading && period !== 'today'} tip="Caricamento dati storici...">
              <Column {...barConfig} height={300} />
            </Spin>
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card title="🔋 Distribuzione Consumo">
            <Pie {...pieConfig} height={300} />
          </Card>
        </Col>
      </Row>

      {/* Tabella riepilogo */}
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <Card title="⚡ Riepilogo Produzione" size="small">
            <Table
              dataSource={[
                { key: '1', voce: 'Energia Generata', valore: `${metrics.production.toFixed(2)} kWh`, icona: '☀️' },
                { key: '2', voce: 'Autoconsumo', valore: `${metrics.selfConsumption.toFixed(2)} kWh`, icona: '🏠' },
                { key: '3', voce: 'Verso Batteria', valore: `${metrics.toBattery.toFixed(2)} kWh`, icona: '🔋' },
                { key: '4', voce: 'Immesso in Rete', valore: `${metrics.toGrid.toFixed(2)} kWh`, icona: '⚡' },
              ]}
              columns={[
                { title: '', dataIndex: 'icona', width: 40 },
                { title: 'Voce', dataIndex: 'voce' },
                { title: 'Valore', dataIndex: 'valore', align: 'right' as const },
              ]}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        
        <Col xs={24} md={12}>
          <Card title="🏠 Riepilogo Consumo" size="small">
            <Table
              dataSource={[
                { key: '1', voce: 'Consumo Totale', valore: `${metrics.consumption.toFixed(2)} kWh`, icona: '⚡' },
                { key: '2', voce: 'Dal Sole', valore: `${metrics.selfConsumption.toFixed(2)} kWh`, icona: '☀️' },
                { key: '3', voce: 'Dalla Batteria', valore: `${metrics.fromBattery.toFixed(2)} kWh`, icona: '🔋' },
                { key: '4', voce: 'Dalla Rete', valore: `${metrics.fromGrid.toFixed(2)} kWh`, icona: '🔌' },
              ]}
              columns={[
                { title: '', dataIndex: 'icona', width: 40 },
                { title: 'Voce', dataIndex: 'voce' },
                { title: 'Valore', dataIndex: 'valore', align: 'right' as const },
              ]}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};
