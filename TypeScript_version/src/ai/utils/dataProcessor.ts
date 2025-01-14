import * as tf from '@tensorflow/tfjs-node';
import { TechnicalIndicators } from './indicators';
import { logger } from '../../utils/logger';

export interface TradeData {
  timestamp: number;
  price: number;
  volume: number;
}

export interface ProcessedData {
  features: tf.Tensor2D;
  labels: tf.Tensor2D;
  featureNames: string[];
}

export class DataProcessor {
  private readonly lookback: number;
  private readonly predictionSteps: number;

  constructor(lookback: number = 30, predictionSteps: number = 5) {
    this.lookback = lookback;
    this.predictionSteps = predictionSteps;
  }

  async processTradeData(data: TradeData[]): Promise<ProcessedData> {
    try {
      const prices = data.map(d => d.price);
      const volumes = data.map(d => d.volume);

      // Calculate technical indicators
      const rsi = TechnicalIndicators.calculateRSI(prices);
      const { macd, signal, histogram } = TechnicalIndicators.calculateMACD(prices);

      // Create feature matrix
      const features: number[][] = [];
      const labels: number[][] = [];

      for (let i = this.lookback; i < prices.length - this.predictionSteps; i++) {
        const featureWindow = [];
        
        // Price features
        for (let j = i - this.lookback; j < i; j++) {
          featureWindow.push(
            this.normalize(prices[j], prices[j - 1]),
            volumes[j],
            rsi[j],
            macd[j],
            signal[j],
            histogram[j]
          );
        }
        
        features.push(featureWindow);
        
        // Calculate future returns for labels
        const futureReturn = (prices[i + this.predictionSteps] - prices[i]) / prices[i];
        labels.push([futureReturn]);
      }

      return {
        features: tf.tensor2d(features),
        labels: tf.tensor2d(labels),
        featureNames: ['price_change', 'volume', 'rsi', 'macd', 'signal', 'histogram']
      };
    } catch (error) {
      logger.error('Error processing trade data:', error);
      throw error;
    }
  }

  private normalize(current: number, previous: number): number {
    return (current - previous) / previous;
  }
} 