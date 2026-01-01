/**
 * Hook for managing user settings
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import { apiClient, UserSettings, UserSettingsUpdate, DeviceInfo, ApiStatus } from '../utils/api';

// Query keys
const SETTINGS_KEY = ['user-settings'];
const DEVICES_KEY = ['settings-devices'];
const API_STATUS_KEY = ['api-status'];

/**
 * Hook to manage user settings
 */
export const useSettings = () => {
  const queryClient = useQueryClient();

  // Query for fetching settings
  const {
    data: settings,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<UserSettings>({
    queryKey: SETTINGS_KEY,
    queryFn: () => apiClient.getSettings(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });

  // Mutation for updating settings
  const updateMutation = useMutation({
    mutationFn: (newSettings: UserSettingsUpdate) => apiClient.updateSettings(newSettings),
    onSuccess: (data) => {
      queryClient.setQueryData(SETTINGS_KEY, data);
      message.success('Impostazioni salvate con successo!');
    },
    onError: (error: any) => {
      console.error('Error saving settings:', error);
      message.error('Errore nel salvataggio delle impostazioni');
    },
  });

  return {
    settings,
    isLoading,
    isError,
    error,
    refetch,
    updateSettings: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
  };
};

/**
 * Hook to get configured devices for settings page
 */
export const useSettingsDevices = () => {
  const {
    data: devices,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<DeviceInfo[]>({
    queryKey: DEVICES_KEY,
    queryFn: () => apiClient.getSettingsDevices(),
    staleTime: 30 * 1000, // 30 seconds
    retry: 2,
  });

  return {
    devices: devices || [],
    isLoading,
    isError,
    error,
    refetch,
  };
};

/**
 * Hook to get ZCS API connection status
 */
export const useApiStatus = () => {
  const {
    data: status,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<ApiStatus>({
    queryKey: API_STATUS_KEY,
    queryFn: () => apiClient.getApiStatus(),
    staleTime: 10 * 1000, // 10 seconds
    refetchInterval: 30 * 1000, // Auto-refresh every 30s
    retry: 1,
  });

  return {
    status,
    isLoading,
    isError,
    error,
    refetch,
  };
};

export default useSettings;
