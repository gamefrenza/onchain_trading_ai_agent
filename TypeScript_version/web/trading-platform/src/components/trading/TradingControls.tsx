import React from 'react';
import { Paper, Button, TextField, Grid, Typography } from '@mui/material';

interface TradingControlsProps {
  onBuy?: () => void;
  onSell?: () => void;
}

const TradingControls: React.FC<TradingControlsProps> = ({ onBuy, onSell }) => {
  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Trading Controls
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Amount"
            type="number"
            variant="outlined"
            size="small"
          />
        </Grid>
        <Grid item xs={6}>
          <Button
            fullWidth
            variant="contained"
            color="success"
            onClick={onBuy}
          >
            Buy
          </Button>
        </Grid>
        <Grid item xs={6}>
          <Button
            fullWidth
            variant="contained"
            color="error"
            onClick={onSell}
          >
            Sell
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default TradingControls; 