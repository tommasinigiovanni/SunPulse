import React, { useMemo } from 'react';
import { Line } from '@ant-design/charts';
import { Card, Empty, Spin, Alert } from 'antd';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import { formatPower, formatTime } from '@/utils/formatters';
import { CHART_CONFIG } from '@/utils/constants';

interface PowerChartProps {
  height?: number;
  title?: string;
  deviceIds?: string[];
  showLegend?: boolean;
  autoRefresh?: boolean;
}

export const PowerChart: React.FC<PowerChartProps> = ({
  height = CHART_CONFIG.HEIGHT.LARGE,
  title = "Produzione vs Consumo",
  deviceIds,
  showLegend = true,
  autoRefresh = true,
}) => {
  const { data: realTimeData, isLoading, error } = useRealTimeData({
    deviceIds,
    enableWebSocket: autoRefresh,
  });

  // Trasforma i dati per il grafico
  const chartData = useMemo(() => {
    if (!realTimeData || realTimeData.length === 0) {
      return [];
    }

    // Simula dati storici per demo (in produzione verrebbero dall'API)
    const now = new Date();
    const dataPoints = [];

    // Genera punti ogni 15 minuti per le ultime 24 ore
    for (let i = 95; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 15 * 60 * 1000);
      const timeString = formatTime(timestamp);
      
      // Calcola produzione basata su dati reali con variazione temporale
      const hour = timestamp.getHours();
      const isDay = hour >= 6 && hour <= 18;
      const sunIntensity = isDay ? Math.sin(((hour - 6) / 12) * Math.PI) : 0;
      
      const totalProduction = realTimeData.reduce((sum, device) => {
        if (device.power && device.power > 0) {
          // Varia la produzione in base all'ora e con un po' di rumore
          const variation = 0.8 + Math.random() * 0.4; // ±20% variation
          return sum + (device.power * sunIntensity * variation);
        }
        return sum;
      }, 0);

      // Simula consumo (più stabile ma con picchi negli orari di punta)
      const baseConsumption = 2000; // 2kW base
      const peakMultiplier = (hour >= 7 && hour <= 9) || (hour >= 18 && hour <= 21) ? 1.5 : 1;
      const consumption = baseConsumption * peakMultiplier * (0.9 + Math.random() * 0.2);

      // Calcola grid (positivo = importazione, negativo = esportazione)
      const grid = consumption - totalProduction;

      dataPoints.push(
        {
          timestamp: timeString,
          value: totalProduction,
          type: 'Produzione',
          category: 'power',
        },
        {
          timestamp: timeString,
          value: consumption,
          type: 'Consumo',
          category: 'power',
        },
        {
          timestamp: timeString,
          value: Math.abs(grid),
          type: grid > 0 ? 'Prelievo Rete' : 'Immissione Rete',
          category: 'grid',
        }
      );
    }

    return dataPoints;
  }, [realTimeData]);

  const config = {
    data: chartData,
    height,
    xField: 'timestamp',
    yField: 'value',
    seriesField: 'type',
    smooth: true,
    animation: {
      appear: {
        animation: 'path-in',
        duration: CHART_CONFIG.ANIMATION_DURATION,
      },
    },
    color: ({ type }: any) => {
      switch (type) {
        case 'Produzione':
          return CHART_CONFIG.COLORS.SUCCESS;
        case 'Consumo':
          return CHART_CONFIG.COLORS.PRIMARY;
        case 'Prelievo Rete':
          return CHART_CONFIG.COLORS.ERROR;
        case 'Immissione Rete':
          return CHART_CONFIG.COLORS.WARNING;
        default:
          return CHART_CONFIG.COLORS.PRIMARY;
      }
    },
    // legend: showLegend, // Temporarily disabled for compilation
    tooltip: {
      formatter: (datum: any) => ({
        name: datum.type,
        value: formatPower(datum.value),
      }),
      shared: true,
      showCrosshairs: true,
    },
    xAxis: {
      type: 'cat',
      tickCount: 8,
      label: {
        autoRotate: true,
      },
    },
    yAxis: {
      label: {
        formatter: (value: string) => formatPower(Number(value)),
      },
      grid: {
        line: {
          style: {
            stroke: '#f0f0f0',
            lineWidth: 1,
          },
        },
      },
    },
    slider: {
      start: 0.8, // Mostra le ultime 20% delle ore (circa 5 ore)
      end: 1,
    },
  };

  // Render states
  if (error) {
    return (
      <Card title={title}>
        <Alert
          message="Errore nel caricamento dei dati"
          description={error.toString()}
          type="error"
          showIcon
        />
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card title={title}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height 
        }}>
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  if (!chartData || chartData.length === 0) {
    return (
      <Card title={title}>
        <Empty 
          description="Nessun dato disponibile"
          style={{ height: height - 100 }}
        />
      </Card>
    );
  }

  return (
    <Card 
      title={title}
      style={{ height: 'auto' }}
    >
      <Line {...config} />
    </Card>
  );
}; 