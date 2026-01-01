import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/utils/api';
import { UPDATE_INTERVALS } from '@/utils/constants';

interface EnergyStats {
  today: number;
  yesterday: number;
  lastWeek: number;
  lastMonth: number;
  efficiency: number;
  variationFromYesterday: number;
  variationFromLastWeek: number;
  variationFromLastMonth: number;
  selfConsumption: number;
  gridExport: number;
}

export const useEnergyStats = () => {
  const [stats, setStats] = useState<EnergyStats>({
    today: 0,
    yesterday: 0,
    lastWeek: 0,
    lastMonth: 0,
    efficiency: 0,
    variationFromYesterday: 0,
    variationFromLastWeek: 0,
    variationFromLastMonth: 0,
    selfConsumption: 0,
    gridExport: 0,
  });

  // Fetch oggi
  const { data: todayData } = useQuery({
    queryKey: ['energy-stats', 'today'],
    queryFn: async () => {
      const now = new Date();
      const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      return apiClient.getSystemHistoricalData(
        startOfDay.toISOString(),
        now.toISOString(),
        '1h',
        'energy'
      );
    },
    refetchInterval: UPDATE_INTERVALS.REALTIME,
    staleTime: UPDATE_INTERVALS.REALTIME / 2,
  });

  // Fetch ieri
  const { data: yesterdayData } = useQuery({
    queryKey: ['energy-stats', 'yesterday'],
    queryFn: async () => {
      const now = new Date();
      const startOfYesterday = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
      const endOfYesterday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      return apiClient.getSystemHistoricalData(
        startOfYesterday.toISOString(),
        endOfYesterday.toISOString(),
        '1h',
        'energy'
      );
    },
    refetchInterval: UPDATE_INTERVALS.DEVICES,
    staleTime: UPDATE_INTERVALS.DEVICES / 2,
  });

  // Fetch settimana scorsa
  const { data: lastWeekData } = useQuery({
    queryKey: ['energy-stats', 'lastWeek'],
    queryFn: async () => {
      const now = new Date();
      const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      return apiClient.getSystemHistoricalData(
        sevenDaysAgo.toISOString(),
        now.toISOString(),
        '1d',
        'energy'
      );
    },
    refetchInterval: UPDATE_INTERVALS.DEVICES,
    staleTime: UPDATE_INTERVALS.DEVICES,
  });

  // Fetch mese scorso
  const { data: lastMonthData } = useQuery({
    queryKey: ['energy-stats', 'lastMonth'],
    queryFn: async () => {
      const now = new Date();
      const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      return apiClient.getSystemHistoricalData(
        thirtyDaysAgo.toISOString(),
        now.toISOString(),
        '1d',
        'energy'
      );
    },
    refetchInterval: UPDATE_INTERVALS.ANALYTICS,
    staleTime: UPDATE_INTERVALS.ANALYTICS,
  });

  // Calcola statistiche quando i dati cambiano
  useEffect(() => {
    if (!todayData && !yesterdayData) return;

    const calculateTotal = (data: any) => {
      if (!data?.data?.timeline) return 0;
      return data.data.timeline.reduce((sum: number, point: any) =>
        sum + (point.production || 0), 0
      );
    };

    const today = calculateTotal(todayData);
    const yesterday = calculateTotal(yesterdayData);
    const lastWeekAvg = calculateTotal(lastWeekData) / 7;
    const lastMonthAvg = calculateTotal(lastMonthData) / 30;

    // Calcola variazioni percentuali
    const variationFromYesterday = yesterday > 0
      ? ((today - yesterday) / yesterday) * 100
      : 0;

    const variationFromLastWeek = lastWeekAvg > 0
      ? ((today - lastWeekAvg) / lastWeekAvg) * 100
      : 0;

    const variationFromLastMonth = lastMonthAvg > 0
      ? ((today - lastMonthAvg) / lastMonthAvg) * 100
      : 0;

    // Calcola efficienza (rapporto tra energia prodotta e attesa teorica)
    // Assumiamo picco teorico di 5kW per 6 ore = 30kWh al giorno
    const theoreticalMax = 30;
    const efficiency = theoreticalMax > 0 ? (today / theoreticalMax) * 100 : 0;

    // Calcola autoconsumo e immissione rete
    const todayTimeline = todayData?.data?.timeline || [];
    const selfConsumption = todayTimeline.reduce((sum: number, point: any) =>
      sum + (point.self_consumed || 0), 0
    );
    const gridExport = todayTimeline.reduce((sum: number, point: any) =>
      sum + (point.grid_export || 0), 0
    );

    setStats({
      today,
      yesterday,
      lastWeek: lastWeekAvg,
      lastMonth: lastMonthAvg,
      efficiency: Math.min(efficiency, 100), // Cap at 100%
      variationFromYesterday,
      variationFromLastWeek,
      variationFromLastMonth,
      selfConsumption: selfConsumption > 0 ? selfConsumption : today * 0.6, // Fallback 60%
      gridExport: gridExport > 0 ? gridExport : today * 0.4, // Fallback 40%
    });
  }, [todayData, yesterdayData, lastWeekData, lastMonthData]);

  const isLoading = !todayData && !yesterdayData;

  return {
    stats,
    isLoading,
  };
};
