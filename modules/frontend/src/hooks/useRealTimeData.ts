import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/utils/api';
import { RealTimeData, RealTimeDataResponse } from '@/types/api';
import { UPDATE_INTERVALS, WS_EVENTS } from '@/utils/constants';

interface UseRealTimeDataOptions {
  deviceIds?: string[];
  enableWebSocket?: boolean;
  pollingInterval?: number;
}

interface WebSocketState {
  connected: boolean;
  lastMessage?: string;
  error?: string;
}

export const useRealTimeData = (options: UseRealTimeDataOptions = {}) => {
  const {
    deviceIds,
    enableWebSocket = import.meta.env.VITE_ENABLE_REALTIME === 'true',
    pollingInterval = UPDATE_INTERVALS.REALTIME,
  } = options;

  const queryClient = useQueryClient();
  const [wsState, setWsState] = useState<WebSocketState>({ connected: false });
  const [realTimeData, setRealTimeData] = useState<RealTimeData[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // Fallback polling per i dati real-time
  const { 
    data: pollingData, 
    isLoading, 
    error: pollingError,
    refetch 
  } = useQuery({
    queryKey: ['realtime-data', deviceIds],
    queryFn: () => apiClient.getRealTimeData(deviceIds),
    refetchInterval: enableWebSocket ? false : pollingInterval,
    staleTime: pollingInterval / 2,
    retry: 3,
  });

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (!enableWebSocket || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connesso');
        setWsState({ connected: true });
        reconnectAttempts.current = 0;

        // Invia subscription per dispositivi specifici
        if (deviceIds && deviceIds.length > 0) {
          wsRef.current?.send(JSON.stringify({
            type: 'subscribe',
            devices: deviceIds,
          }));
        }
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setWsState(prev => ({ ...prev, lastMessage: event.data }));

          switch (message.type) {
            case WS_EVENTS.REALTIME_UPDATE:
              if (message.payload) {
                setRealTimeData(prev => {
                  const newData = Array.isArray(message.payload) 
                    ? message.payload 
                    : [message.payload];
                  
                  // Aggiorna o aggiungi dati per device
                  const updatedData = [...prev];
                  newData.forEach((newItem: RealTimeData) => {
                    const existingIndex = updatedData.findIndex(
                      item => item.device_id === newItem.device_id
                    );
                    if (existingIndex >= 0) {
                      updatedData[existingIndex] = newItem;
                    } else {
                      updatedData.push(newItem);
                    }
                  });
                  
                  return updatedData;
                });
                
                // Invalida cache query per triggerare re-render
                queryClient.invalidateQueries({ queryKey: ['realtime-data'] });
              }
              break;

            case WS_EVENTS.DEVICE_STATUS:
              // Aggiorna stato dispositivo
              if (message.payload?.device_id) {
                setRealTimeData(prev => 
                  prev.map(item => 
                    item.device_id === message.payload.device_id
                      ? { ...item, status: message.payload.status }
                      : item
                  )
                );
              }
              break;

            case WS_EVENTS.CONNECTION_STATUS:
              console.log('WebSocket status:', message.payload);
              break;

            default:
              console.log('Messaggio WebSocket non gestito:', message.type);
          }
        } catch (error) {
          console.error('Errore parsing messaggio WebSocket:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnesso:', event.code, event.reason);
        setWsState({ connected: false, error: event.reason });
        
        // Riconnessione automatica
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            connectWebSocket();
          }, delay);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('Errore WebSocket:', error);
        setWsState(prev => ({ 
          ...prev, 
          error: 'Errore di connessione WebSocket' 
        }));
      };

    } catch (error) {
      console.error('Errore creazione WebSocket:', error);
      setWsState({ 
        connected: false, 
        error: 'Impossibile creare connessione WebSocket' 
      });
    }
  }, [enableWebSocket, deviceIds, queryClient]);

  // Disconnetti WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setWsState({ connected: false });
  }, []);

  // Effetto per gestire connessione WebSocket
  useEffect(() => {
    if (enableWebSocket) {
      connectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [enableWebSocket, connectWebSocket, disconnectWebSocket]);

  // Effetto per subscription changes
  useEffect(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN && deviceIds) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        devices: deviceIds,
      }));
    }
  }, [deviceIds]);

  // Combina dati WebSocket e polling
  const combinedData = realTimeData.length > 0 ? realTimeData : pollingData?.devices || [];
  
  // Usa summary dall'API se disponibile, altrimenti calcolalo (con memoization per evitare loop)
  const summary = useMemo(() => {
    return pollingData?.summary || {
      total_power: combinedData.reduce((sum, item) => sum + (item.power || 0), 0),
      total_energy_today: combinedData.reduce((sum, item) => sum + (item.energy_today || 0), 0),
      online_devices: combinedData.filter(item => item.status === 'online').length,
      total_devices: combinedData.length,
    };
  }, [pollingData?.summary, combinedData]);

  // Metodi di controllo
  const reconnect = useCallback(() => {
    disconnectWebSocket();
    setTimeout(connectWebSocket, 1000);
  }, [connectWebSocket, disconnectWebSocket]);

  const refreshData = useCallback(() => {
    refetch();
  }, [refetch]);

  return {
    // Dati
    data: combinedData,
    summary,
    
    // Stato loading e errori
    isLoading: isLoading && realTimeData.length === 0,
    error: pollingError || wsState.error,
    
    // Stato WebSocket
    isWebSocketConnected: wsState.connected,
    webSocketStatus: wsState,
    
    // Metodi di controllo
    reconnect,
    refreshData,
    disconnect: disconnectWebSocket,
    
    // Utilità
    lastUpdate: pollingData?.timestamp || wsState.lastMessage,
    dataSource: realTimeData.length > 0 ? 'websocket' : 'polling',
  };
}; 