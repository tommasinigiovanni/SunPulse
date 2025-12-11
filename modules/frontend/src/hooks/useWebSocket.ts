import { useState, useEffect, useRef, useCallback } from 'react';
import { WS_EVENTS } from '@/utils/constants';

interface WebSocketOptions {
  url?: string;
  protocols?: string | string[];
  autoConnect?: boolean;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
}

interface WebSocketState {
  connected: boolean;
  connecting: boolean;
  error?: string;
  lastMessage?: any;
  reconnectAttempts: number;
}

type MessageHandler = (data: any) => void;
type EventHandler = (event: Event) => void;

export const useWebSocket = (options: WebSocketOptions = {}) => {
  const {
    url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
    protocols,
    autoConnect = true,
    maxReconnectAttempts = 5,
    reconnectInterval = 1000,
    heartbeatInterval = 30000,
  } = options;

  const [state, setState] = useState<WebSocketState>({
    connected: false,
    connecting: false,
    reconnectAttempts: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout>();
  const messageHandlersRef = useRef<Map<string, MessageHandler[]>>(new Map());
  const eventHandlersRef = useRef<Map<string, EventHandler[]>>(new Map());

  // Registra handler per messaggi
  const on = useCallback((eventType: string, handler: MessageHandler) => {
    const handlers = messageHandlersRef.current.get(eventType) || [];
    handlers.push(handler);
    messageHandlersRef.current.set(eventType, handlers);

    // Ritorna funzione per unsubscribe
    return () => {
      const currentHandlers = messageHandlersRef.current.get(eventType) || [];
      const index = currentHandlers.indexOf(handler);
      if (index > -1) {
        currentHandlers.splice(index, 1);
        messageHandlersRef.current.set(eventType, currentHandlers);
      }
    };
  }, []);

  // Registra handler per eventi WebSocket
  const addEventListener = useCallback((eventType: string, handler: EventHandler) => {
    const handlers = eventHandlersRef.current.get(eventType) || [];
    handlers.push(handler);
    eventHandlersRef.current.set(eventType, handlers);

    return () => {
      const currentHandlers = eventHandlersRef.current.get(eventType) || [];
      const index = currentHandlers.indexOf(handler);
      if (index > -1) {
        currentHandlers.splice(index, 1);
        eventHandlersRef.current.set(eventType, currentHandlers);
      }
    };
  }, []);

  // Invia messaggio
  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      wsRef.current.send(message);
      return true;
    }
    console.warn('WebSocket non connesso, impossibile inviare messaggio');
    return false;
  }, []);

  // Heartbeat per mantenere connessione viva
  const startHeartbeat = useCallback(() => {
    if (heartbeatInterval > 0) {
      heartbeatTimeoutRef.current = setInterval(() => {
        send({ type: 'ping' });
      }, heartbeatInterval);
    }
  }, [heartbeatInterval, send]);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearInterval(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = undefined;
    }
  }, []);

  // Connessione WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setState(prev => ({ ...prev, connecting: true, error: undefined }));

    try {
      wsRef.current = new WebSocket(url, protocols);

      wsRef.current.onopen = (event) => {
        console.log('WebSocket connesso a:', url);
        setState(prev => ({
          ...prev,
          connected: true,
          connecting: false,
          reconnectAttempts: 0,
          error: undefined,
        }));

        startHeartbeat();

        // Trigger event handlers
        const handlers = eventHandlersRef.current.get('open') || [];
        handlers.forEach(handler => handler(event));
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          setState(prev => ({ ...prev, lastMessage: data }));

          // Handle pong response
          if (data.type === 'pong') {
            return;
          }

          // Trigger message handlers
          const handlers = messageHandlersRef.current.get(data.type) || [];
          handlers.forEach(handler => handler(data));

          // Trigger generic message handlers
          const allHandlers = messageHandlersRef.current.get('*') || [];
          allHandlers.forEach(handler => handler(data));

        } catch (error) {
          console.error('Errore parsing messaggio WebSocket:', error);
        }

        // Trigger event handlers
        const handlers = eventHandlersRef.current.get('message') || [];
        handlers.forEach(handler => handler(event));
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnesso:', event.code, event.reason);
        
        setState(prev => ({
          ...prev,
          connected: false,
          connecting: false,
          error: event.reason || 'Connessione chiusa',
        }));

        stopHeartbeat();

        // Riconnessione automatica
        if (state.reconnectAttempts < maxReconnectAttempts && event.code !== 1000) {
          const delay = Math.min(reconnectInterval * Math.pow(2, state.reconnectAttempts), 30000);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            setState(prev => ({ ...prev, reconnectAttempts: prev.reconnectAttempts + 1 }));
            connect();
          }, delay);
        }

        // Trigger event handlers
        const handlers = eventHandlersRef.current.get('close') || [];
        handlers.forEach(handler => handler(event));
      };

      wsRef.current.onerror = (event) => {
        console.error('Errore WebSocket:', event);
        
        setState(prev => ({
          ...prev,
          connecting: false,
          error: 'Errore di connessione WebSocket',
        }));

        // Trigger event handlers
        const handlers = eventHandlersRef.current.get('error') || [];
        handlers.forEach(handler => handler(event));
      };

    } catch (error) {
      console.error('Errore creazione WebSocket:', error);
      setState(prev => ({
        ...prev,
        connecting: false,
        error: 'Impossibile creare connessione WebSocket',
      }));
    }
  }, [url, protocols, maxReconnectAttempts, reconnectInterval, startHeartbeat, stopHeartbeat]);

  // Disconnessione
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = undefined;
    }

    stopHeartbeat();

    if (wsRef.current) {
      wsRef.current.close(1000, 'Disconnessione manuale');
      wsRef.current = null;
    }

    setState({
      connected: false,
      connecting: false,
      reconnectAttempts: 0,
    });
  }, [stopHeartbeat]);

  // Riconnessione manuale
  const reconnect = useCallback(() => {
    disconnect();
    setTimeout(connect, 100);
  }, [disconnect, connect]);

  // Auto-connect effect
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    // Stato
    ...state,
    readyState: wsRef.current?.readyState,
    
    // Metodi
    connect,
    disconnect,
    reconnect,
    send,
    
    // Event handlers
    on,
    addEventListener,
    
    // Utility
    isConnecting: state.connecting,
    isConnected: state.connected,
    canSend: state.connected && wsRef.current?.readyState === WebSocket.OPEN,
  };
}; 