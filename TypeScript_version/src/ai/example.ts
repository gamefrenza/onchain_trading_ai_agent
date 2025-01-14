import { DataProcessor, TradeData } from './utils/dataProcessor';
import { DeepLearningModel } from './models/deepLearningModel';
import { Backtester } from './backtesting/backtest';
import { logger } from '../utils/logger';

async function trainAndEvaluateModel(historicalData: TradeData[]) {
  try {
    // Initialize data processor
    const dataProcessor = new DataProcessor(30, 5);
    const processedData = await dataProcessor.processTradeData(historicalData);

    // Initialize and build model
    const model = new DeepLearningModel({
      learningRate: 0.001,
      epochs: 100,
      batchSize: 32,
      validationSplit: 0.2,
    });

    await model.build([30, 6]); // 30 timesteps, 6 features per timestep

    // Train model
    const history = await model.train(processedData);
    logger.info('Training completed');

    // Make predictions
    const predictions = await model.predict(processedData.features);
    
    // Run backtest
    const backtester = new Backtester(10000, 0.001);
    const results = await backtester.runBacktest(
      historicalData,
      Array.from(predictions.dataSync()),
      0.001
    );

    logger.info('Backtest results:', results);

    // Save model
    await model.save('./models/trading_model');

    return results;
  } catch (error) {
    logger.error('Error in model training and evaluation:', error);
    throw error;
  }
} 