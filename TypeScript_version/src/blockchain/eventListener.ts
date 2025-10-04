import { ethers } from 'ethers';
import { CONFIG } from '../utils/config';
import { logger } from '../utils/logger';
import { DEX_ABI, TradeEvent, SwapEvent } from './contracts/dexInterface';
import { retry } from '../utils/retry';

export class BlockchainEventListener {
  private provider: ethers.WebSocketProvider;
  private contracts: Map<string, ethers.Contract>;
  private reconnectAttempts: number = 0;
  private readonly MAX_RECONNECT_ATTEMPTS = 5;

  constructor() {
    this.contracts = new Map();
    this.initializeProvider();
  }

  private initializeProvider() {
    try {
      const wsUrl = CONFIG.BLOCKCHAIN.WS_URL;
      this.provider = new ethers.WebSocketProvider(wsUrl);
      this.setupProviderEventHandlers();
    } catch (error) {
      logger.error('Failed to initialize WebSocket provider:', error);
      this.handleReconnection();
    }
  }

  private setupProviderEventHandlers() {
    // ethers v6 does not expose the underlying ws client; rely on provider events
    this.provider.on('close', () => {
      logger.warn('WebSocket connection closed');
      this.handleReconnection();
    });
    this.provider.on('error', (error) => {
      logger.error('WebSocket error:', error);
      this.handleReconnection();
    });
  }

  private async handleReconnection() {
    if (this.reconnectAttempts < this.MAX_RECONNECT_ATTEMPTS) {
      this.reconnectAttempts++;
      logger.info(`Attempting to reconnect... (${this.reconnectAttempts}/${this.MAX_RECONNECT_ATTEMPTS})`);
      
      await retry(async () => {
        this.initializeProvider();
        await this.initializeContracts();
      }, {
        retries: 3,
        delay: 1000 * Math.pow(2, this.reconnectAttempts), // Exponential backoff
      });
    } else {
      logger.error('Max reconnection attempts reached');
      throw new Error('Failed to maintain WebSocket connection');
    }
  }

  async initializeContracts() {
    try {
      for (const pair of CONFIG.TRADING.TRADING_PAIRS) {
        const [token0, token1] = pair.split('-');
        const contractAddress = CONFIG.DEX.PAIRS[pair];
        
        if (!contractAddress) {
          logger.error(`No contract address found for pair ${pair}`);
          continue;
        }

        const contract = new ethers.Contract(
          contractAddress,
          DEX_ABI,
          this.provider
        );

        this.contracts.set(pair, contract);
        logger.info(`Initialized contract for pair ${pair}`);
      }
    } catch (error) {
      logger.error('Failed to initialize contracts:', error);
      throw error;
    }
  }

  async startListening() {
    try {
      for (const [pair, contract] of this.contracts) {
        this.listenToTradeEvents(pair, contract);
        this.listenToSwapEvents(pair, contract);
      }
      logger.info('Started listening to blockchain events');
    } catch (error) {
      logger.error('Failed to start listening to events:', error);
      throw error;
    }
  }

  private listenToTradeEvents(pair: string, contract: ethers.Contract) {
    contract.on('Trade', async (maker, taker, pairAddress, amount, price, timestamp, event) => {
      try {
        const tradeEvent: TradeEvent = {
          maker,
          taker,
          pair: pairAddress,
          amount: ethers.formatEther(amount),
          price: ethers.formatEther(price),
          timestamp: Number(timestamp),
          transactionHash: event.transactionHash,
          blockNumber: event.blockNumber,
        };

        await this.processTrade(pair, tradeEvent);
      } catch (error) {
        logger.error(`Error processing trade event for pair ${pair}:`, error);
      }
    });
  }

  private listenToSwapEvents(pair: string, contract: ethers.Contract) {
    contract.on('Swap', async (sender, amount0In, amount1In, amount0Out, amount1Out, to, event) => {
      try {
        const swapEvent: SwapEvent = {
          sender,
          amount0In: ethers.formatEther(amount0In),
          amount1In: ethers.formatEther(amount1In),
          amount0Out: ethers.formatEther(amount0Out),
          amount1Out: ethers.formatEther(amount1Out),
          to,
          transactionHash: event.transactionHash,
          blockNumber: event.blockNumber,
        };

        await this.processSwap(pair, swapEvent);
      } catch (error) {
        logger.error(`Error processing swap event for pair ${pair}:`, error);
      }
    });
  }

  private async processTrade(pair: string, trade: TradeEvent) {
    logger.info(`Processing trade for ${pair}:`, {
      transactionHash: trade.transactionHash,
      amount: trade.amount,
      price: trade.price,
    });
    // Implement trade processing logic (e.g., store in database, trigger analysis)
  }

  private async processSwap(pair: string, swap: SwapEvent) {
    logger.info(`Processing swap for ${pair}:`, {
      transactionHash: swap.transactionHash,
      amount0In: swap.amount0In,
      amount1Out: swap.amount1Out,
    });
    // Implement swap processing logic
  }

  async stop() {
    try {
      for (const [pair, contract] of this.contracts) {
        contract.removeAllListeners();
      }
      await this.provider.destroy();
      logger.info('Stopped blockchain event listener');
    } catch (error) {
      logger.error('Error stopping blockchain event listener:', error);
      throw error;
    }
  }
} 