import { ethers } from 'ethers';
import { CONFIG } from '../utils/config';
import { logger } from '../utils/logger';

export class Web3Client {
  private provider: ethers.JsonRpcProvider;
  private wallet: ethers.Wallet;

  constructor() {
    try {
      this.provider = new ethers.JsonRpcProvider(CONFIG.BLOCKCHAIN.RPC_URL);
      this.wallet = new ethers.Wallet(CONFIG.BLOCKCHAIN.PRIVATE_KEY, this.provider);
    } catch (error) {
      logger.error('Failed to initialize Web3 client:', error);
      throw error;
    }
  }

  async getBalance(address: string): Promise<string> {
    try {
      const balance = await this.provider.getBalance(address);
      return ethers.formatEther(balance);
    } catch (error) {
      logger.error('Failed to get balance:', error);
      throw error;
    }
  }

  async sendTransaction(to: string, value: string): Promise<ethers.TransactionResponse> {
    try {
      const tx = await this.wallet.sendTransaction({
        to,
        value: ethers.parseEther(value),
      });
      return tx;
    } catch (error) {
      logger.error('Failed to send transaction:', error);
      throw error;
    }
  }
} 