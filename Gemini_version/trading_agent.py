from web3 import Web3
import pandas as pd
import numpy as np
import logging
import time
from datetime import datetime, timedelta
from decimal import Decimal
import json
from technical_indicators import TechnicalAnalysis
from ml_trading_signals import MLSignalGenerator
from contract_trader import ContractTrader
from uniswap_data_fetcher import UniswapDataFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='trading_agent.log'
)

class TradingAgent:
    def __init__(self, config_path='trading_config.json'):
        """
        Initialize the trading agent with configuration parameters
        """
        try:
            # Load configuration
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            # Initialize components
            self.data_fetcher = UniswapDataFetcher()
            self.trader = ContractTrader()
            
            # Trading state
            self.current_position = None
            self.position_entry_price = None
            self.last_trade_time = None
            
            # Load trading parameters
            self.load_trading_parameters()
            
            logging.info("Successfully initialized TradingAgent")
            
        except Exception as e:
            logging.error(f"Initialization error: {str(e)}")
            raise

    def load_trading_parameters(self):
        """
        Load trading parameters from config
        """
        try:
            # Risk management parameters
            self.stop_loss_pct = self.config['risk_management']['stop_loss_percentage']
            self.take_profit_pct = self.config['risk_management']['take_profit_percentage']
            self.max_position_size = Decimal(str(self.config['risk_management']['max_position_size']))
            self.min_position_size = Decimal(str(self.config['risk_management']['min_position_size']))
            
            # Trading parameters
            self.trading_interval = self.config['trading']['interval_seconds']
            self.confidence_threshold = self.config['trading']['confidence_threshold']
            self.max_slippage = self.config['trading']['max_slippage']
            
            # Token addresses
            self.token_address = self.config['tokens']['trading_token_address']
            
            logging.info("Loaded trading parameters from config")
            
        except Exception as e:
            logging.error(f"Error loading trading parameters: {str(e)}")
            raise

    def fetch_and_analyze_data(self):
        """
        Fetch recent market data and perform technical analysis
        """
        try:
            # Fetch recent trading data
            current_block = self.data_fetcher.w3.eth.block_number
            from_block = current_block - self.config['data']['blocks_to_analyze']
            
            df = self.data_fetcher.fetch_swap_events(from_block)
            
            # Perform technical analysis
            ta = TechnicalAnalysis(df)
            ta.add_all_indicators()
            df_with_indicators = ta.get_dataframe()
            
            # Generate ML signals
            ml_signals = MLSignalGenerator(df_with_indicators)
            ml_signals.generate_labels()
            model, _ = ml_signals.train_model()
            
            # Get latest prediction
            latest_signals = ml_signals.generate_trading_signals()
            latest_signal = latest_signals.iloc[-1]
            
            return latest_signal, df_with_indicators.iloc[-1]
            
        except Exception as e:
            logging.error(f"Error in data analysis: {str(e)}")
            raise

    def check_risk_management(self, current_price):
        """
        Check if any risk management rules are triggered
        """
        try:
            if self.current_position is None or self.position_entry_price is None:
                return None
                
            price_change_pct = (current_price - self.position_entry_price) / self.position_entry_price * 100
            
            # Check stop loss
            if self.current_position == 'long' and price_change_pct <= -self.stop_loss_pct:
                logging.info(f"Stop loss triggered at {price_change_pct:.2f}%")
                return 'sell'
                
            # Check take profit
            if self.current_position == 'long' and price_change_pct >= self.take_profit_pct:
                logging.info(f"Take profit triggered at {price_change_pct:.2f}%")
                return 'sell'
                
            return None
            
        except Exception as e:
            logging.error(f"Error in risk management check: {str(e)}")
            raise

    def calculate_position_size(self, signal_strength):
        """
        Calculate position size based on signal strength and risk parameters
        """
        try:
            # Base position size on signal strength and max position size
            position_size = self.max_position_size * Decimal(str(signal_strength))
            
            # Ensure within limits
            position_size = min(position_size, self.max_position_size)
            position_size = max(position_size, self.min_position_size)
            
            return position_size
            
        except Exception as e:
            logging.error(f"Error calculating position size: {str(e)}")
            raise

    def execute_trading_decision(self, signal, current_price):
        """
        Execute trading decision based on signal and risk management
        """
        try:
            # Check risk management first
            risk_action = self.check_risk_management(current_price)
            if risk_action == 'sell' and self.current_position is not None:
                # Execute risk management trade
                receipt = self.trader.execute_trade(
                    action='sell',
                    token_address=self.token_address,
                    amount=self.current_position_size,
                    max_slippage=self.max_slippage
                )
                self.current_position = None
                self.position_entry_price = None
                logging.info(f"Risk management trade executed: {receipt['transactionHash'].hex()}")
                return
            
            # Process new trading signal
            if signal['probability'] >= self.confidence_threshold:
                if self.current_position is None:  # No position, consider buying
                    position_size = self.calculate_position_size(signal['probability'])
                    receipt = self.trader.execute_trade(
                        action='buy',
                        token_address=self.token_address,
                        amount=position_size,
                        max_slippage=self.max_slippage
                    )
                    self.current_position = 'long'
                    self.position_entry_price = current_price
                    self.current_position_size = position_size
                    self.last_trade_time = datetime.now()
                    logging.info(f"Buy trade executed: {receipt['transactionHash'].hex()}")
                    
            elif signal['probability'] <= (1 - self.confidence_threshold):
                if self.current_position == 'long':  # Exit long position
                    receipt = self.trader.execute_trade(
                        action='sell',
                        token_address=self.token_address,
                        amount=self.current_position_size,
                        max_slippage=self.max_slippage
                    )
                    self.current_position = None
                    self.position_entry_price = None
                    logging.info(f"Sell trade executed: {receipt['transactionHash'].hex()}")
                    
        except Exception as e:
            logging.error(f"Error executing trading decision: {str(e)}")
            raise

    def run(self):
        """
        Main trading loop
        """
        try:
            logging.info("Starting trading agent...")
            
            while True:
                try:
                    # Fetch and analyze data
                    signal, current_data = self.fetch_and_analyze_data()
                    current_price = current_data['Close']
                    
                    # Execute trading decision
                    self.execute_trading_decision(signal, current_price)
                    
                    # Log current state
                    self.log_trading_state(signal, current_price)
                    
                    # Wait for next interval
                    time.sleep(self.trading_interval)
                    
                except Exception as e:
                    logging.error(f"Error in trading loop: {str(e)}")
                    time.sleep(60)  # Wait before retrying
                    
        except KeyboardInterrupt:
            logging.info("Trading agent stopped by user")
        except Exception as e:
            logging.error(f"Fatal error in trading agent: {str(e)}")
            raise

    def log_trading_state(self, signal, current_price):
        """
        Log current trading state and metrics
        """
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'current_price': float(current_price),
                'signal_probability': float(signal['probability']),
                'current_position': self.current_position,
                'position_entry_price': float(self.position_entry_price) if self.position_entry_price else None,
                'pnl_pct': float((current_price - self.position_entry_price) / self.position_entry_price * 100) 
                    if self.position_entry_price else None
            }
            
            logging.info(f"Trading State: {json.dumps(state, indent=2)}")
            
        except Exception as e:
            logging.error(f"Error logging trading state: {str(e)}")


def main():
    """
    Example usage of TradingAgent
    """
    try:
        agent = TradingAgent()
        agent.run()
        
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 