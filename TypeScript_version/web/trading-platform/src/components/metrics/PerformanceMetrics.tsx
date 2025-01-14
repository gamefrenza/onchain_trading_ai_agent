import React from 'react';
import { Paper, Grid, Typography } from '@mui/material';

interface MetricProps {
  label: string;
  value: string | number;
}

const Metric: React.FC<MetricProps> = ({ label, value }) => (
  <Grid item xs={6} md={3}>
    <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h6">
        {value}
      </Typography>
    </Paper>
  </Grid>
);

interface PerformanceMetricsProps {
  totalProfit?: number;
  winRate?: number;
  tradesCount?: number;
  averageReturn?: number;
}

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({
  totalProfit = 0,
  winRate = 0,
  tradesCount = 0,
  averageReturn = 0,
}) => {
  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Performance Metrics
      </Typography>
      <Grid container spacing={2}>
        <Metric 
          label="Total Profit"
          value={`$${totalProfit.toFixed(2)}`}
        />
        <Metric 
          label="Win Rate"
          value={`${(winRate * 100).toFixed(1)}%`}
        />
        <Metric 
          label="Total Trades"
          value={tradesCount}
        />
        <Metric 
          label="Avg. Return"
          value={`${(averageReturn * 100).toFixed(1)}%`}
        />
      </Grid>
    </Paper>
  );
};

export default PerformanceMetrics; 