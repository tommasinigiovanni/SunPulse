import React, { useMemo, useEffect, useState, useRef, memo } from 'react';
import { Line } from '@ant-design/charts';
import { Card, Empty, Spin, Alert } from 'antd';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import { apiClient } from '@/utils/api';
import { formatPower, formatTime } from '@/utils/formatters';
import { CHART_CONFIG } from '@/utils/constants';

interface PowerChartProps {
  height?: number;
  title?: string;
  deviceIds?: string[];
  showLegend?: boolean;
  autoRefresh?: boolean;
}

// Componente interno memorizzato per evitare re-render
const MemoizedLine = memo(Line, (prevProps, nextProps) => {
  // Confronta solo i dati, non l'intera config
  return JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data);
});

export const PowerChart: React.FC<PowerChartProps> = ({
  height = CHART_CONFIG.HEIGHT.LARGE,
  title = "Produzione vs Consumo",
  deviceIds,
  showLegend = true,
  autoRefresh = true,
}) => {
  // Carica dati solo una volta all'avvio, poi usa cache
  const { data: realTimeData, isLoading, error } = useRealTimeData({
    deviceIds,
    enableWebSocket: false, // Disabilita WebSocket per evitare refresh continui
    pollingInterval: 60000, // Polling ogni 60 secondi invece di 10
  });
  
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [historicalLoading, setHistoricalLoading] = useState(false);
  
  // Mantieni lo stato dello slider con ref per evitare re-render
  const sliderRangeRef = useRef<[number, number]>([0.7, 1]);
  
  // Flag per sapere se è il primo render (per animazioni)
  const isFirstRender = useRef(true);
  
  // Cache dei dati simulati per evitare rigenerazione ad ogni poll
  const simulatedDataRef = useRef<any[]>([]);
  const lastEnergyRef = useRef<number>(0);
  
  // Ref per il plot instance
  const plotRef = useRef<any>(null);

  // Carica dati storici dall'API
  useEffect(() => {
    const fetchHistoricalData = async () => {
      try {
        setHistoricalLoading(true);
        const now = new Date();
        const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        
        const response = await apiClient.getSystemHistoricalData(
          yesterday.toISOString(),
          now.toISOString(),
          '15m',
          'power'
        );
        
        if (response?.data?.timeline && response.data.timeline.length > 0) {
          setHistoricalData(response.data.timeline);
        }
      } catch (err) {
        console.warn('Dati storici non disponibili, uso simulazione:', err);
        // Fallback silenzioso ai dati simulati
      } finally {
        setHistoricalLoading(false);
      }
    };

    fetchHistoricalData();
  }, []);

  // Trasforma i dati per il grafico (con cache per evitare rigenerazione)
  const chartData = useMemo(() => {
    // Se abbiamo dati storici reali dall'API, usali
    if (historicalData.length > 0) {
      return historicalData.flatMap((point: any) => [
        {
          timestamp: formatTime(new Date(point.timestamp)),
          value: point.production || 0,
          type: 'Produzione',
          category: 'power',
        },
        {
          timestamp: formatTime(new Date(point.timestamp)),
          value: point.consumption || 0,
          type: 'Consumo',
          category: 'power',
        },
        {
          timestamp: formatTime(new Date(point.timestamp)),
          value: Math.abs((point.consumption || 0) - (point.production || 0)),
          type: (point.consumption || 0) > (point.production || 0) ? 'Prelievo Rete' : 'Immissione Rete',
          category: 'grid',
        }
      ]);
    }

    // Fallback: genera dati simulati basati sui dati real-time
    if (!realTimeData || realTimeData.length === 0) {
      return simulatedDataRef.current.length > 0 ? simulatedDataRef.current : [];
    }

    // Calcola energia totale prodotta oggi (kWh)
    const totalEnergyToday = realTimeData.reduce((sum, device) => 
      sum + (device.energy_today || 0), 0);
    
    // Usa cache se energia non è cambiata significativamente (evita rigenerazione)
    if (simulatedDataRef.current.length > 0 && Math.abs(totalEnergyToday - lastEnergyRef.current) < 0.1) {
      return simulatedDataRef.current;
    }
    
    // Aggiorna riferimento energia
    lastEnergyRef.current = totalEnergyToday;

    const now = new Date();
    const dataPoints = [];
    
    // Stima potenza di picco: energia giornaliera / ore di sole effettive (~6h)
    const estimatedPeakPower = totalEnergyToday > 0 ? (totalEnergyToday / 5) * 1000 : 3000; // Watt

    // Genera punti ogni 15 minuti per le ultime 24 ore (simulazione)
    for (let i = 95; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 15 * 60 * 1000);
      const timeString = formatTime(timestamp);
      
      // Calcola produzione basata su curva solare realistica
      const hour = timestamp.getHours();
      const isDay = hour >= 7 && hour <= 17; // Ore di sole effettive
      
      // Curva a campana per simulare produzione solare
      let sunIntensity = 0;
      if (isDay) {
        // Picco a mezzogiorno (ora 12)
        const hoursFromNoon = Math.abs(hour - 12);
        sunIntensity = Math.max(0, 1 - (hoursFromNoon / 6) ** 2);
      }
      
      // Variazione deterministica basata sul timestamp (non random)
      const seed = (timestamp.getHours() * 60 + timestamp.getMinutes()) / 1440;
      const variation = 0.85 + seed * 0.3;
      
      const production = estimatedPeakPower * sunIntensity * variation;

      // Simula consumo reale dalla rete (powerConsuming dai dati)
      const baseConsumption = realTimeData[0]?.raw_data?.realtimeData?.params?.value?.[0]?.[realTimeData[0]?.thing_key]?.powerConsuming || 2000;
      const peakMultiplier = (hour >= 7 && hour <= 9) || (hour >= 18 && hour <= 21) ? 1.3 : 1;
      const nightMultiplier = (hour >= 0 && hour <= 6) || (hour >= 22 && hour <= 23) ? 0.7 : 1;
      const consumption = baseConsumption * peakMultiplier * nightMultiplier * (0.9 + seed * 0.2);

      // Calcola grid (positivo = importazione, negativo = esportazione)
      const grid = consumption - production;

      dataPoints.push(
        {
          timestamp: timeString,
          value: Math.round(production),
          type: 'Produzione',
          category: 'power',
        },
        {
          timestamp: timeString,
          value: Math.round(consumption),
          type: 'Consumo',
          category: 'power',
        },
        {
          timestamp: timeString,
          value: Math.round(Math.abs(grid)),
          type: grid > 0 ? 'Prelievo Rete' : 'Immissione Rete',
          category: 'grid',
        }
      );
    }

    // Salva in cache
    simulatedDataRef.current = dataPoints;
    return dataPoints;
  }, [realTimeData, historicalData]);

  // Filtra solo Produzione e Consumo (rimuovi Prelievo/Immissione Rete per semplificare)
  const filteredChartData = chartData.filter((d: any) => 
    d.type === 'Produzione' || d.type === 'Consumo'
  );

  // Memorizza la config per evitare re-render
  const config = useMemo(() => ({
    data: filteredChartData,
    height,
    xField: 'timestamp',
    yField: 'value',
    seriesField: 'type',
    smooth: true,
    // Disabilita animazioni dopo il primo render
    animation: isFirstRender.current ? {
      appear: {
        animation: 'path-in',
        duration: CHART_CONFIG.ANIMATION_DURATION,
      },
    } : false,
    color: ['#52c41a', '#1890ff'], // Verde per Produzione, Blu per Consumo
    legend: {
      position: 'top' as const,
    },
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
        style: {
          fontSize: 11,
        },
      },
    },
    yAxis: {
      label: {
        formatter: (value: string) => formatPower(Number(value)),
        style: {
          fontSize: 11,
        },
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
      start: sliderRangeRef.current[0],
      end: sliderRangeRef.current[1],
    },
    onReady: (plot: any) => {
      plotRef.current = plot;
      isFirstRender.current = false;
      
      // Gestisci evento slider change
      plot.on('slider:change', (e: any) => {
        if (e.view) {
          sliderRangeRef.current = [e.view.start ?? 0.7, e.view.end ?? 1];
        }
      });
    },
    lineStyle: {
      lineWidth: 2,
    },
  }), [filteredChartData, height]);

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

  if (isLoading || historicalLoading) {
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
      <MemoizedLine {...config} />
    </Card>
  );
}; 