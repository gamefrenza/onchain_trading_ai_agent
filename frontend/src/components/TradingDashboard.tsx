import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { Chart } from './Chart';
import { TradeControls } from './TradeControls';
import { PerformanceMetrics } from './PerformanceMetrics';
import { StrategyConfig } from './StrategyConfig';

interface TradingDashboardProps {
    token: string;
}

export const TradingDashboard: React.FC<TradingDashboardProps> = ({ token }) => {
    const [predictions, setPredictions] = useState<any>(null);
    const [performance, setPerformance] = useState<any>(null);
    
    // WebSocket connections
    const tradesWs = useWebSocket('ws://localhost:8000/ws/trades', {
        onMessage: (data) => {
            // Handle trade updates
        }
    });
    
    const predictionsWs = useWebSocket('ws://localhost:8000/ws/predictions', {
        onMessage: (data) => {
            setPredictions(data);
        }
    });
    
    useEffect(() => {
        // Fetch initial data
        fetchPerformanceMetrics();
    }, []);
    
    const fetchPerformanceMetrics = async () => {
        try {
            const response = await fetch('/api/performance', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();
            setPerformance(data);
        } catch (error) {
            console.error('Error fetching performance metrics:', error);
        }
    };
    
    return (
        <div className="trading-dashboard">
            <div className="dashboard-header">
                <h1>AI Trading Dashboard</h1>
                <PerformanceMetrics data={performance} />
            </div>
            
            <div className="dashboard-main">
                <div className="chart-container">
                    <Chart predictions={predictions} />
                </div>
                
                <div className="controls-container">
                    <TradeControls token={token} />
                    <StrategyConfig token={token} />
                </div>
            </div>
        </div>
    );
}; 