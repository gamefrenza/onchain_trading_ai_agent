import { logger } from '../../utils/logger';

export class TechnicalIndicators {
  static calculateRSI(prices: number[], period: number = 14): number[] {
    try {
      const deltas = prices.slice(1).map((price, i) => price - prices[i]);
      const gains = deltas.map(delta => delta > 0 ? delta : 0);
      const losses = deltas.map(delta => delta < 0 ? -delta : 0);

      let avgGain = gains.slice(0, period).reduce((a, b) => a + b) / period;
      let avgLoss = losses.slice(0, period).reduce((a, b) => a + b) / period;

      const rsi = [100 - (100 / (1 + avgGain / avgLoss))];

      for (let i = period; i < prices.length - 1; i++) {
        avgGain = (avgGain * (period - 1) + gains[i]) / period;
        avgLoss = (avgLoss * (period - 1) + losses[i]) / period;
        rsi.push(100 - (100 / (1 + avgGain / avgLoss)));
      }

      return rsi;
    } catch (error) {
      logger.error('Error calculating RSI:', error);
      throw error;
    }
  }

  static calculateMACD(prices: number[], fastPeriod: number = 12, slowPeriod: number = 26, signalPeriod: number = 9): {
    macd: number[];
    signal: number[];
    histogram: number[];
  } {
    try {
      const fastEMA = this.calculateEMA(prices, fastPeriod);
      const slowEMA = this.calculateEMA(prices, slowPeriod);
      const macd = fastEMA.map((fast, i) => fast - slowEMA[i]);
      const signal = this.calculateEMA(macd, signalPeriod);
      const histogram = macd.map((value, i) => value - signal[i]);

      return { macd, signal, histogram };
    } catch (error) {
      logger.error('Error calculating MACD:', error);
      throw error;
    }
  }

  private static calculateEMA(prices: number[], period: number): number[] {
    const multiplier = 2 / (period + 1);
    const ema = [prices[0]];

    for (let i = 1; i < prices.length; i++) {
      ema.push(
        (prices[i] - ema[i - 1]) * multiplier + ema[i - 1]
      );
    }

    return ema;
  }
} 