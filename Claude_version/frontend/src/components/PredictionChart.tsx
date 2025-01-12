import React from 'react';
import { Line } from 'react-chartjs-2';
import { PredictionData } from '../types';

interface PredictionChartProps {
    predictions: PredictionData[];
    actualPrices: number[];
    timeframes: string[];
}

export const PredictionChart: React.FC<PredictionChartProps> = ({
    predictions,
    actualPrices,
    timeframes
}) => {
    const chartData = {
        labels: timeframes,
        datasets: [
            {
                label: 'Actual Price',
                data: actualPrices,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            },
            {
                label: 'AI Prediction',
                data: predictions.map(p => p.value),
                borderColor: 'rgb(255, 99, 132)',
                borderDash: [5, 5],
                tension: 0.1
            },
            {
                label: 'Confidence Interval',
                data: predictions.map(p => p.confidence),
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderWidth: 0,
                fill: true
            }
        ]
    };

    return (
        <div className="prediction-chart">
            <h3>Price Predictions</h3>
            <Line data={chartData} options={{
                responsive: true,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context: any) => {
                                return `${context.dataset.label}: $${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                }
            }} />
        </div>
    );
}; 