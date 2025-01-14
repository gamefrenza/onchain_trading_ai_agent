import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography } from '@mui/material';
import TradingChart from '../components/trading/TradingChart';
import TradingControls from '../components/trading/TradingControls';
import AIPredictor from '../components/ai/AIPredictor';
import PerformanceMetrics from '../components/metrics/PerformanceMetrics';
import { useWebSocket } from '../contexts/WebSocketContext';

interface TradeData {
  timestamp: number;
  price: number;
  volume: number;
}

interface Prediction {
  timestamp: number;
  predictedPrice: number;
  confidence: number;
}

const Dashboard: React.FC = () => {
  const [trades, setTrades] = useState<TradeData[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const { socket, isConnected } = useWebSocket();

  useEffect(() => {
    if (socket) {
      socket.on('trade', (trade: TradeData) => {
        setTrades(prev => [...prev, trade].slice(-100));
      });

      socket.on('prediction', (prediction: Prediction) => {
        setPredictions(prev => [...prev, prediction].slice(-100));
      });
    }
  }, [socket]);

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4">Trading Dashboard</Typography>
      </Grid>
      
      <Grid item xs={12} md={8}>
        <Paper>
          <TradingChart trades={trades} predictions={predictions} />
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <Paper>
          <AIPredictor predictions={predictions} />
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper>
          <TradingControls />
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper>
          <PerformanceMetrics trades={trades} />
        </Paper>
      </Grid>
    </Grid>
  );
};

export default Dashboard; 