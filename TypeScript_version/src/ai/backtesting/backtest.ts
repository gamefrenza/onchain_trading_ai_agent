import { TradeData } from '../utils/dataProcessor';
import { logger } from '../../utils/logger';

export interface BacktestResult {
  totalReturns: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  trades: {
    timestamp: number;
    type: 'buy' | 'sell';
    price: number;
    returns: number;
  }[];
}

export class Backtester {
  private readonly initialCapital: number;
  private readonly tradingFee: number;

  constructor(initialCapital: number = 10000, tradingFee: number = 0.001) {
    this.initialCapital = initialCapital;
    this.tradingFee = tradingFee;
  }

  async runBacktest(
    data: TradeData[],
    predictions: number[],
    threshold: number = 0.001
  ): Promise<BacktestResult> {
    try {
      let capital = this.initialCapital;
      let position = 0;
      const trades = [];
      const returns = [];

      for (let i = 0; i < predictions.length; i++) {
        const prediction = predictions[i];
        const currentPrice = data[i].price;

        if (prediction > threshold && position === 0) {
          // Buy signal
          position = capital / currentPrice * (1 - this.tradingFee);
          trades.push({
            timestamp: data[i].timestamp,
            type: 'buy',
            price: currentPrice,
            returns: 0,
          });
        } else if (prediction < -threshold && position > 0) {
          // Sell signal
          const tradeReturn = (position * currentPrice * (1 - this.tradingFee)) - capital;
          capital = position * currentPrice * (1 - this.tradingFee);
          position = 0;
          returns.push(tradeReturn / this.initialCapital);
          trades.push({
            timestamp: data[i].timestamp,
            type: 'sell',
            price: currentPrice,
            returns: tradeReturn,
          });
        }
      }

      const totalReturns = (capital - this.initialCapital) / this.initialCapital;
      const sharpeRatio = this.calculateSharpeRatio(returns);
      const maxDrawdown = this.calculateMaxDrawdown(returns);
      const winRate = returns.filter(r => r > 0).length / returns.length;

      return {
        totalReturns,
        sharpeRatio,
        maxDrawdown,
        winRate,
        trades,
      };
    } catch (error) {
      logger.error('Error running backtest:', error);
      throw error;
    }
  }

  private calculateSharpeRatio(returns: number[]): number {
    const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / returns.length;
    const stdDev = Math.sqrt(variance);
    return mean / stdDev * Math.sqrt(252); // Annualized Sharpe Ratio
  }

  private calculateMaxDrawdown(returns: number[]): number {
    let peak = -Infinity;
    let maxDrawdown = 0;

    for (const ret of returns) {
      if (ret > peak) peak = ret;
      const drawdown = peak - ret;
      if (drawdown > maxDrawdown) maxDrawdown = drawdown;
    }

    return maxDrawdown;
  }
} 