import { useList, useOne, useCreate, useUpdate, useDelete } from "@refinedev/core";
import { useMemo } from 'react';
import { Device, DeviceFilters, DeviceType, DeviceStatus } from '@/types/device';
import { DEVICE_TYPES, DEVICE_STATUS } from '@/utils/constants';

interface UseDevicesOptions {
  filters?: DeviceFilters;
  pagination?: {
    current?: number;
    pageSize?: number;
  };
  sorters?: Array<{
    field: string;
    order: 'asc' | 'desc';
  }>;
}

export const useDevices = (options: UseDevicesOptions = {}) => {
  const { filters, pagination, sorters } = options;

  // Lista dispositivi con filtri
  const { 
    data: deviceList, 
    isLoading, 
    error, 
    refetch,
    isRefetching 
  } = useList<Device>({
    resource: "devices",
    pagination: {
      current: pagination?.current || 1,
      pageSize: pagination?.pageSize || 20,
    },
    filters: filters ? Object.entries(filters)
      .filter(([_, value]) => value !== undefined && value !== null)
      .map(([field, value]) => ({
        field,
        operator: Array.isArray(value) ? "in" : "eq",
        value,
      })) : undefined,
    sorters: sorters || [{ field: "name", order: "asc" }],
  });

  const devices = deviceList?.data || [];
  const total = deviceList?.total || 0;

  // Statistiche dispositivi
  const deviceStats = useMemo(() => {
    const stats = {
      total: devices.length,
      online: 0,
      offline: 0,
      warning: 0,
      maintenance: 0,
      error: 0,
      by_type: {} as Record<DeviceType, number>,
      by_status: {} as Record<DeviceStatus, number>,
    };

    devices.forEach(device => {
      // Conta per status
      stats[device.status as keyof typeof stats]++;
      stats.by_status[device.status] = (stats.by_status[device.status] || 0) + 1;
      
      // Conta per tipo
      stats.by_type[device.type] = (stats.by_type[device.type] || 0) + 1;
    });

    return stats;
  }, [devices]);

  // Metodi di filtro e ricerca
  const getDevicesByType = (type: DeviceType) => 
    devices.filter(device => device.type === type);

  const getDevicesByStatus = (status: DeviceStatus) => 
    devices.filter(device => device.status === status);

  const getOnlineDevices = () => 
    devices.filter(device => device.status === DEVICE_STATUS.ONLINE);

  const getOfflineDevices = () => 
    devices.filter(device => device.status === DEVICE_STATUS.OFFLINE);

  const getDevicesWithAlarms = () => 
    devices.filter(device => false); // Temporarily disabled - device.alarms && device.alarms.length > 0);

  const searchDevices = (query: string) => 
    devices.filter(device => 
      device.name.toLowerCase().includes(query.toLowerCase()) ||
      device.serial_number.toLowerCase().includes(query.toLowerCase()) ||
      device.model?.toLowerCase().includes(query.toLowerCase()) ||
      device.manufacturer?.toLowerCase().includes(query.toLowerCase())
    );

  // Calcoli energetici
  const energyStats = useMemo(() => {
    return {
      total_power: devices.reduce((sum, device) => sum + (device.current_power || 0), 0),
      daily_energy: devices.reduce((sum, device) => sum + (device.daily_energy || 0), 0),
      total_energy: devices.reduce((sum, device) => sum + (device.total_energy || 0), 0),
    };
  }, [devices]);

  return {
    // Dati principali
    devices,
    total,
    isLoading,
    error,
    refetch,
    isRefetching,
    
    // Statistiche
    stats: deviceStats,
    energyStats,
    
    // Metodi di filtro
    getDevicesByType,
    getDevicesByStatus,
    getOnlineDevices,
    getOfflineDevices,
    getDevicesWithAlarms,
    searchDevices,
  };
};

// Hook per singolo dispositivo
export const useDevice = (id: string) => {
  const { data, isLoading, error, refetch } = useOne<Device>({
    resource: "devices",
    id,
  });

  return {
    device: data?.data,
    isLoading,
    error,
    refetch,
  };
};

// Hook per operazioni CRUD dispositivi
export const useDeviceActions = () => {
  const { mutate: createDevice, isLoading: isCreating } = useCreate<Device>();
  const { mutate: updateDevice, isLoading: isUpdating } = useUpdate<Device>();
  const { mutate: deleteDevice, isLoading: isDeleting } = useDelete();

  const create = async (deviceData: Partial<Device>) => {
    return new Promise((resolve, reject) => {
      createDevice(
        {
          resource: "devices",
          values: deviceData,
        },
        {
          onSuccess: (data) => resolve(data.data),
          onError: (error) => reject(error),
        }
      );
    });
  };

  const update = async (id: string, deviceData: Partial<Device>) => {
    return new Promise((resolve, reject) => {
      updateDevice(
        {
          resource: "devices",
          id,
          values: deviceData,
        },
        {
          onSuccess: (data) => resolve(data.data),
          onError: (error) => reject(error),
        }
      );
    });
  };

  const remove = async (id: string) => {
    return new Promise((resolve, reject) => {
      deleteDevice(
        {
          resource: "devices",
          id,
        },
        {
          onSuccess: () => resolve(true),
          onError: (error) => reject(error),
        }
      );
    });
  };

  return {
    create,
    update,
    remove,
    isCreating,
    isUpdating,
    isDeleting,
  };
}; 