import { Position, StrategyConfig } from '../strategies/types';
import { logger } from '../../utils/logger';

export class RiskManager {
  private readonly config: StrategyConfig;
  private accountBalance: number;

  constructor(config: StrategyConfig, initialBalance: number) {
    this.config = config;
    this.accountBalance = initialBalance;
  }

  calculatePositionSize(price: number, stopLoss: number): number {
    try {
      const riskAmount = this.accountBalance * (this.config.riskPerTrade / 100);
      const stopLossDistance = Math.abs(price - stopLoss);
      const positionSize = riskAmount / stopLossDistance;

      // Apply maximum position size constraint
      return Math.min(
        positionSize,
        this.accountBalance * (this.config.maxPositionSize / 100) / price
      );
    } catch (error) {
      logger.error('Error calculating position size:', error);
      throw error;
    }
  }

  calculateStopLoss(entryPrice: number, type: 'long' | 'short'): number {
    const stopLossDistance = entryPrice * (this.config.stopLossPercent / 100);
    return type === 'long' 
      ? entryPrice - stopLossDistance 
      : entryPrice + stopLossDistance;
  }

  calculateTakeProfit(entryPrice: number, type: 'long' | 'short'): number {
    const takeProfitDistance = entryPrice * (this.config.takeProfitPercent / 100);
    return type === 'long'
      ? entryPrice + takeProfitDistance
      : entryPrice - takeProfitDistance;
  }

  validateTrade(signal: TradeSignal, openPositions: Position[]): boolean {
    try {
      // Check confidence score
      if (signal.confidence < this.config.minConfidenceScore) {
        logger.info('Trade rejected: Low confidence score');
        return false;
      }

      // Check maximum open positions
      if (openPositions.length >= this.config.maxOpenPositions) {
        logger.info('Trade rejected: Maximum open positions reached');
        return false;
      }

      // Check if enough balance available
      const requiredMargin = this.calculateRequiredMargin(signal.price);
      if (this.getAvailableBalance() < requiredMargin) {
        logger.info('Trade rejected: Insufficient balance');
        return false;
      }

      return true;
    } catch (error) {
      logger.error('Error validating trade:', error);
      throw error;
    }
  }

  private calculateRequiredMargin(price: number): number {
    return price * this.config.maxPositionSize / 100;
  }

  getAvailableBalance(): number {
    return this.accountBalance;
  }

  updateBalance(newBalance: number): void {
    this.accountBalance = newBalance;
    logger.info(`Account balance updated: ${newBalance}`);
  }
} 