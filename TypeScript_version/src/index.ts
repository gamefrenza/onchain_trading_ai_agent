import { TradingEngine } from './trading/tradingEngine';
import { logger } from './utils/logger';

async function main(): Promise<void> {
  try {
    const engine = new TradingEngine();
    await engine.startTrading();
  } catch (error) {
    logger.error('Fatal error starting engine', error);
    process.exit(1);
  }
}

main();


