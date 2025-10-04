import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';

interface WebSocketOptions {
    onMessage?: (data: any) => void;
    onError?: (error: Event) => void;
    reconnectAttempts?: number;
    reconnectInterval?: number;
}

export const useWebSocket = (url: string, options: WebSocketOptions = {}) => {
    if (!url.startsWith('wss://') && !url.startsWith('ws://')) {
        throw new Error('Invalid WebSocket URL protocol');
    }

    const { token } = useAuth();
    if (!token) {
        throw new Error('Authentication token required for WebSocket connection');
    }

    const [ws, setWs] = useState<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    
    const connect = useCallback(() => {
        let retryCount = 0;
        const maxRetries = options.reconnectAttempts || 5;
        let connectionTimeout: ReturnType<typeof setTimeout>;

        const attemptConnection = () => {
            if (retryCount >= maxRetries) {
                options.onError?.(new Error('Max retry attempts reached'));
                return;
            }

            const wsInstance = new WebSocket(`${url}?token=${encodeURIComponent(token)}`);
            
            wsInstance.onopen = () => {
                clearTimeout(connectionTimeout);
                setIsConnected(true);
            };
            
            wsInstance.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data && typeof data === 'object') {
                        options.onMessage?.(data);
                    }
                } catch (error) {
                    console.error('Invalid message format:', error);
                }
            };
            
            wsInstance.onerror = (error) => {
                options.onError?.(error);
                console.error('WebSocket error:', error);
            };
            
            wsInstance.onclose = () => {
                setIsConnected(false);
                retryCount++;
                setTimeout(attemptConnection, Math.min(1000 * Math.pow(2, retryCount), 30000));
            };
            
            setWs(wsInstance);
        };

        attemptConnection();
    }, [url, token, options]);
    
    useEffect(() => {
        connect();
        return () => {
            ws?.close();
        };
    }, [connect]);
    
    return { ws, isConnected };
}; 