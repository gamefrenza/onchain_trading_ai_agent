import dotenv from 'dotenv';

dotenv.config();

export const CONFIG = {
  BLOCKCHAIN: {
    RPC_URL: process.env.RPC_URL || 'http://localhost:8545',
    PRIVATE_KEY: process.env.PRIVATE_KEY || '',
    CHAIN_ID: parseInt(process.env.CHAIN_ID || '1'),
    WS_URL: process.env.WS_URL || 'wss://mainnet.infura.io/ws/v3/your-project-id',
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
  DEX: {
    PAIRS: {
      'ETH-USDT': '0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852', // Example Uniswap V2 pair
      'BTC-USDT': '0x0000000000000000000000000000000000000000', // Add actual address
    },
  },
}; 