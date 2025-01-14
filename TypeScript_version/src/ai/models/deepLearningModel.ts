import * as tf from '@tensorflow/tfjs-node';
import { ProcessedData } from '../utils/dataProcessor';
import { logger } from '../../utils/logger';

export interface ModelConfig {
  learningRate: number;
  epochs: number;
  batchSize: number;
  validationSplit: number;
}

export class DeepLearningModel {
  private model: tf.LayersModel | null = null;
  private readonly config: ModelConfig;

  constructor(config: ModelConfig) {
    this.config = config;
  }

  async build(inputShape: number[]): Promise<void> {
    try {
      this.model = tf.sequential({
        layers: [
          tf.layers.lstm({
            units: 50,
            returnSequences: true,
            inputShape: inputShape,
          }),
          tf.layers.dropout({ rate: 0.2 }),
          tf.layers.lstm({
            units: 30,
            returnSequences: false,
          }),
          tf.layers.dropout({ rate: 0.2 }),
          tf.layers.dense({ units: 1, activation: 'linear' }),
        ],
      });

      const optimizer = tf.train.adam(this.config.learningRate);
      
      this.model.compile({
        optimizer,
        loss: 'meanSquaredError',
        metrics: ['mse', 'mae'],
      });

      logger.info('Model built successfully');
    } catch (error) {
      logger.error('Error building model:', error);
      throw error;
    }
  }

  async train(data: ProcessedData): Promise<tf.History> {
    if (!this.model) {
      throw new Error('Model not built');
    }

    try {
      const history = await this.model.fit(data.features, data.labels, {
        epochs: this.config.epochs,
        batchSize: this.config.batchSize,
        validationSplit: this.config.validationSplit,
        callbacks: {
          onEpochEnd: (epoch, logs) => {
            logger.info(`Epoch ${epoch + 1} - loss: ${logs?.loss.toFixed(4)} - val_loss: ${logs?.val_loss.toFixed(4)}`);
          },
        },
      });

      return history;
    } catch (error) {
      logger.error('Error training model:', error);
      throw error;
    }
  }

  async predict(features: tf.Tensor2D): Promise<tf.Tensor> {
    if (!this.model) {
      throw new Error('Model not built');
    }

    try {
      return this.model.predict(features) as tf.Tensor;
    } catch (error) {
      logger.error('Error making prediction:', error);
      throw error;
    }
  }

  async save(path: string): Promise<void> {
    if (!this.model) {
      throw new Error('Model not built');
    }

    try {
      await this.model.save(`file://${path}`);
      logger.info(`Model saved to ${path}`);
    } catch (error) {
      logger.error('Error saving model:', error);
      throw error;
    }
  }

  async load(path: string): Promise<void> {
    try {
      this.model = await tf.loadLayersModel(`file://${path}`);
      logger.info(`Model loaded from ${path}`);
    } catch (error) {
      logger.error('Error loading model:', error);
      throw error;
    }
  }
} 