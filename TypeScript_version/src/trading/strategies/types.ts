import { TradeData } from '../../ai/utils/dataProcessor';

export interface Position {
  entryPrice: number;
  size: number;
  stopLoss: number;
  takeProfit: number;
  timestamp: number;
  type: 'long' | 'short';
}

export interface StrategyMetrics {
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  winRate: number;
  averageReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  profitFactor: number;
}

export interface StrategyConfig {
  maxPositionSize: number;
  riskPerTrade: number;  // Percentage of account to risk per trade
  stopLossPercent: number;
  takeProfitPercent: number;
  minConfidenceScore: number;
  maxOpenPositions: number;
}

export interface TradeSignal {
  type: 'buy' | 'sell' | 'hold';
  confidence: number;
  price: number;
  timestamp: number;
} 