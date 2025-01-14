import winston from 'winston';
import { CONFIG } from './config';

export const logger = winston.createLogger({
  level: CONFIG.LOGGING.LEVEL,
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
}); 