import { TradeSignal, Position, StrategyMetrics, StrategyConfig } from './types';
import { RiskManager } from '../risk/riskManager';
import { DeepLearningModel } from '../../ai/models/deepLearningModel';
import { TechnicalIndicators } from '../../ai/utils/indicators';
import { logger } from '../../utils/logger';

export class AITrendStrategy {
  private readonly model: DeepLearningModel;
  private readonly riskManager: RiskManager;
  private readonly config: StrategyConfig;
  private openPositions: Position[] = [];
  private tradeHistory: Position[] = [];

  constructor(
    model: DeepLearningModel,
    config: StrategyConfig,
    initialBalance: number
  ) {
    this.model = model;
    this.config = config;
    this.riskManager = new RiskManager(config, initialBalance);
  }

  async analyzeMarket(marketData: any): Promise<TradeSignal> {
    try {
      // Get AI model prediction
      const prediction = await this.model.predict(marketData);
      const predictionValue = (await prediction.data())[0];

      // Calculate technical indicators
      const prices = marketData.map((d: any) => d.price);
      const rsi = TechnicalIndicators.calculateRSI(prices).slice(-1)[0];
      const { macd } = TechnicalIndicators.calculateMACD(prices);
      const latestMACD = macd.slice(-1)[0];

      // Combine signals
      const signal = this.generateSignal(predictionValue, rsi, latestMACD, prices.slice(-1)[0]);
      
      logger.info('Market analysis completed', {
        prediction: predictionValue,
        rsi,
        macd: latestMACD,
        signal,
      });

      return signal;
    } catch (error) {
      logger.error('Error analyzing market:', error);
      throw error;
    }
  }

  private generateSignal(
    prediction: number,
    rsi: number,
    macd: number,
    currentPrice: number
  ): TradeSignal {
    const confidence = Math.abs(prediction);
    
    let type: 'buy' | 'sell' | 'hold' = 'hold';
    
    if (prediction > 0 && rsi < 70 && macd > 0) {
      type = 'buy';
    } else if (prediction < 0 && rsi > 30 && macd < 0) {
      type = 'sell';
    }

    return {
      type,
      confidence,
      price: currentPrice,
      timestamp: Date.now(),
    };
  }

  async executeTrade(signal: TradeSignal): Promise<void> {
    try {
      if (!this.riskManager.validateTrade(signal, this.openPositions)) {
        return;
      }

      const stopLoss = this.riskManager.calculateStopLoss(
        signal.price,
        signal.type === 'buy' ? 'long' : 'short'
      );

      const positionSize = this.riskManager.calculatePositionSize(
        signal.price,
        stopLoss
      );

      const takeProfit = this.riskManager.calculateTakeProfit(
        signal.price,
        signal.type === 'buy' ? 'long' : 'short'
      );

      const position: Position = {
        entryPrice: signal.price,
        size: positionSize,
        stopLoss,
        takeProfit,
        timestamp: signal.timestamp,
        type: signal.type === 'buy' ? 'long' : 'short',
      };

      this.openPositions.push(position);
      logger.info('Trade executed', position);
    } catch (error) {
      logger.error('Error executing trade:', error);
      throw error;
    }
  }

  async updatePositions(currentPrice: number): Promise<void> {
    try {
      for (const position of this.openPositions) {
        if (this.shouldClosePosition(position, currentPrice)) {
          await this.closePosition(position, currentPrice);
        }
      }
    } catch (error) {
      logger.error('Error updating positions:', error);
      throw error;
    }
  }

  private shouldClosePosition(position: Position, currentPrice: number): boolean {
    if (position.type === 'long') {
      return currentPrice <= position.stopLoss || currentPrice >= position.takeProfit;
    } else {
      return currentPrice >= position.stopLoss || currentPrice <= position.takeProfit;
    }
  }

  private async closePosition(position: Position, currentPrice: number): Promise<void> {
    const pnl = this.calculatePnL(position, currentPrice);
    this.riskManager.updateBalance(this.riskManager.getAvailableBalance() + pnl);
    
    this.tradeHistory.push({
      ...position,
      exitPrice: currentPrice,
      pnl,
    });

    this.openPositions = this.openPositions.filter(p => p !== position);
    logger.info('Position closed', { position, pnl });
  }

  private calculatePnL(position: Position, currentPrice: number): number {
    const priceChange = currentPrice - position.entryPrice;
    return position.type === 'long'
      ? priceChange * position.size
      : -priceChange * position.size;
  }

  getMetrics(): StrategyMetrics {
    const winningTrades = this.tradeHistory.filter(t => t.pnl > 0).length;
    const totalTrades = this.tradeHistory.length;
    const returns = this.tradeHistory.map(t => t.pnl);

    return {
      totalTrades,
      winningTrades,
      losingTrades: totalTrades - winningTrades,
      winRate: winningTrades / totalTrades,
      averageReturn: returns.reduce((a, b) => a + b, 0) / totalTrades,
      sharpeRatio: this.calculateSharpeRatio(returns),
      maxDrawdown: this.calculateMaxDrawdown(returns),
      profitFactor: this.calculateProfitFactor(returns),
    };
  }

  private calculateSharpeRatio(returns: number[]): number {
    const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / returns.length;
    return mean / Math.sqrt(variance) * Math.sqrt(252);
  }

  private calculateMaxDrawdown(returns: number[]): number {
    let peak = 0;
    let maxDrawdown = 0;
    let runningTotal = 0;

    for (const ret of returns) {
      runningTotal += ret;
      if (runningTotal > peak) peak = runningTotal;
      const drawdown = peak - runningTotal;
      if (drawdown > maxDrawdown) maxDrawdown = drawdown;
    }

    return maxDrawdown;
  }

  private calculateProfitFactor(returns: number[]): number {
    const profits = returns.filter(r => r > 0).reduce((a, b) => a + b, 0);
    const losses = Math.abs(returns.filter(r => r < 0).reduce((a, b) => a + b, 0));
    return profits / losses;
  }
} 