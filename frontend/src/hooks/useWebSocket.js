import { useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for WebSocket connection to the IGNIS alerts stream.
 * Automatically reconnects on disconnect with exponential backoff.
 */
export default function useWebSocket(url, onMessage) {
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const retryCount = useRef(0);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('🔌 WebSocket connected to alerts stream');
        retryCount.current = 0;
      };

      ws.onmessage = (event) => {
        console.log('🚨 Alert received:', event.data);
        if (onMessage) {
          try {
            const data = JSON.parse(event.data);
            onMessage(data);
          } catch {
            onMessage(event.data);
          }
        }
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        const delay = Math.min(1000 * 2 ** retryCount.current, 30000);
        retryCount.current += 1;
        reconnectTimer.current = setTimeout(connect, delay);
      };

      ws.onerror = (err) => {
        console.warn('WebSocket error:', err);
        ws.close();
      };

      wsRef.current = ws;
    } catch (e) {
      console.warn('WebSocket connection failed:', e);
    }
  }, [url, onMessage]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);

  return wsRef;
}
