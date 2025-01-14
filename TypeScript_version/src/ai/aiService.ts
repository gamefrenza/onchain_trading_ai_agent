import axios from 'axios';
import { CONFIG } from '../utils/config';
import { logger } from '../utils/logger';

export class AIService {
  private readonly apiKey: string;
  private readonly endpoint: string;

  constructor() {
    this.apiKey = CONFIG.AI.API_KEY;
    this.endpoint = CONFIG.AI.MODEL_ENDPOINT;
  }

  async getPrediction(data: any): Promise<any> {
    try {
      const response = await axios.post(
        this.endpoint,
        data,
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      logger.error('Failed to get AI prediction:', error);
      throw error;
    }
  }
} 