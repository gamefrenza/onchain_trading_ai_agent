import React from 'react';
import { PerformanceData } from '../types';

interface PerformanceMetricsProps {
    data: PerformanceData;
}

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ data }) => {
    return (
        <div className="performance-metrics">
            <h3>Performance Overview</h3>
            <div className="metrics-grid">
                <div className="metric-card">
                    <h4>Total Return</h4>
                    <span className={`value ${data.totalReturn >= 0 ? 'positive' : 'negative'}`}>
                        {data.totalReturn.toFixed(2)}%
                    </span>
                </div>
                
                <div className="metric-card">
                    <h4>Win Rate</h4>
                    <span className="value">{(data.winRate * 100).toFixed(1)}%</span>
                </div>
                
                <div className="metric-card">
                    <h4>Sharpe Ratio</h4>
                    <span className="value">{data.sharpeRatio.toFixed(2)}</span>
                </div>
                
                <div className="metric-card">
                    <h4>Max Drawdown</h4>
                    <span className="value negative">{data.maxDrawdown.toFixed(2)}%</span>
                </div>
            </div>
        </div>
    );
}; 