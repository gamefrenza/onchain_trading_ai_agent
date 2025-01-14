import dotenv from 'dotenv';

dotenv.config();

export const CONFIG = {
  BLOCKCHAIN: {
    RPC_URL: process.env.RPC_URL || 'http://localhost:8545',
    PRIVATE_KEY: process.env.PRIVATE_KEY || '',
    CHAIN_ID: parseInt(process.env.CHAIN_ID || '1'),
  },
  AI: {
    MODEL_ENDPOINT: process.env.AI_MODEL_ENDPOINT || '',
    API_KEY: process.env.AI_API_KEY || '',
  },
  TRADING: {
    MIN_TRADE_AMOUNT: process.env.MIN_TRADE_AMOUNT || '0.1',
    MAX_TRADE_AMOUNT: process.env.MAX_TRADE_AMOUNT || '1.0',
    TRADING_PAIRS: (process.env.TRADING_PAIRS || 'ETH-USDT').split(','),
  },
  LOGGING: {
    LEVEL: process.env.LOG_LEVEL || 'info',
  },
}; 