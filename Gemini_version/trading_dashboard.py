import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import json
import logging
from decimal import Decimal

from trading_agent import TradingAgent
from technical_indicators import TechnicalAnalysis
from uniswap_data_fetcher import UniswapDataFetcher
from contract_trader import ContractTrader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='dashboard.log'
)

class TradingDashboard:
    def __init__(self):
        """
        Initialize the dashboard components
        """
        try:
            # Load configuration
            with open('trading_config.json', 'r') as f:
                self.config = json.load(f)
            
            # Initialize components
            self.agent = TradingAgent()
            self.data_fetcher = UniswapDataFetcher()
            self.trader = ContractTrader()
            
            # Cache for performance
            self.last_data_fetch = None
            self.cached_data = None
            self.cache_duration = 60  # seconds
            
            logging.info("Dashboard initialized successfully")
            
        except Exception as e:
            logging.error(f"Dashboard initialization error: {str(e)}")
            raise

    def fetch_latest_data(self):
        """
        Fetch latest market data with caching
        """
        try:
            current_time = time.time()
            
            # Return cached data if still valid
            if (self.last_data_fetch is not None and 
                current_time - self.last_data_fetch < self.cache_duration and 
                self.cached_data is not None):
                return self.cached_data
            
            # Fetch new data as OHLCV
            current_block = self.data_fetcher.w3.eth.block_number
            from_block = current_block - self.config['data']['blocks_to_analyze']

            df = self.data_fetcher.fetch_ohlcv(from_block)

            # Add technical indicators
            ta = TechnicalAnalysis(df)
            ta.add_all_indicators()
            df_with_indicators = ta.get_dataframe()
            
            # Update cache
            self.cached_data = df_with_indicators
            self.last_data_fetch = current_time
            
            return df_with_indicators
            
        except Exception as e:
            logging.error(f"Error fetching latest data: {str(e)}")
            st.error(f"Error fetching data: {str(e)}")
            return None

    def create_price_chart(self, df):
        """
        Create interactive price chart with indicators
        """
        try:
            fig = make_subplots(rows=2, cols=1, shared_xaxis=True, 
                              vertical_spacing=0.03,
                              row_heights=[0.7, 0.3])
            
            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ), row=1, col=1)
            
            # Add Moving Averages
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA_21'],
                name='SMA 21',
                line=dict(color='blue', width=1)
            ), row=1, col=1)
            
            # Add Bollinger Bands
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_Upper'],
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash')
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_Lower'],
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty'
            ), row=1, col=1)
            
            # Volume bars
            fig.add_trace(go.Bar(
                x=df.index, y=df['Volume'],
                name='Volume'
            ), row=2, col=1)
            
            # Update layout
            fig.update_layout(
                title='Price and Volume Chart',
                yaxis_title='Price',
                yaxis2_title='Volume',
                xaxis_rangeslider_visible=False,
                height=600
            )
            
            return fig
            
        except Exception as e:
            logging.error(f"Error creating price chart: {str(e)}")
            st.error(f"Error creating chart: {str(e)}")
            return None

    def create_indicators_chart(self, df):
        """
        Create technical indicators chart
        """
        try:
            fig = make_subplots(rows=2, cols=1, shared_xaxis=True,
                              vertical_spacing=0.03,
                              row_heights=[0.5, 0.5])
            
            # RSI
            fig.add_trace(go.Scatter(
                x=df.index, y=df['RSI'],
                name='RSI'
            ), row=1, col=1)
            
            # Add RSI overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)
            
            # MACD
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD'],
                name='MACD'
            ), row=2, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD_Signal'],
                name='Signal'
            ), row=2, col=1)
            
            fig.add_trace(go.Bar(
                x=df.index, y=df['MACD_Hist'],
                name='MACD Histogram'
            ), row=2, col=1)
            
            # Update layout
            fig.update_layout(
                title='Technical Indicators',
                height=500
            )
            
            return fig
            
        except Exception as e:
            logging.error(f"Error creating indicators chart: {str(e)}")
            st.error(f"Error creating indicators chart: {str(e)}")
            return None

    def display_trading_metrics(self):
        """
        Display current trading metrics and position information
        """
        try:
            # Create columns for metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Current Position",
                    value=self.agent.current_position or "No Position"
                )
            
            with col2:
                if self.agent.position_entry_price:
                    current_price = self.cached_data['Close'].iloc[-1]
                    pnl_pct = ((current_price - self.agent.position_entry_price) / 
                              self.agent.position_entry_price * 100)
                    st.metric(
                        label="Current P&L",
                        value=f"{pnl_pct:.2f}%",
                        delta=f"{pnl_pct:.2f}%"
                    )
                else:
                    st.metric(label="Current P&L", value="N/A")
            
            with col3:
                st.metric(
                    label="Last Trade Time",
                    value=self.agent.last_trade_time.strftime('%Y-%m-%d %H:%M:%S')
                    if self.agent.last_trade_time else "N/A"
                )
            
        except Exception as e:
            logging.error(f"Error displaying metrics: {str(e)}")
            st.error(f"Error displaying metrics: {str(e)}")

    def manual_trading_controls(self):
        """
        Display manual trading controls
        """
        try:
            st.sidebar.header("Manual Trading Controls")
            
            # Amount input
            amount = st.sidebar.number_input(
                "Trade Amount (ETH)",
                min_value=0.0,
                max_value=float(self.agent.max_position_size),
                value=float(self.agent.min_position_size),
                step=0.1
            )
            
            # Slippage tolerance
            slippage = st.sidebar.slider(
                "Slippage Tolerance (%)",
                min_value=0.1,
                max_value=5.0,
                value=1.0,
                step=0.1
            )
            
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                if st.button("Buy"):
                    self.execute_manual_trade('buy', Decimal(str(amount)), slippage/100)
            
            with col2:
                if st.button("Sell"):
                    self.execute_manual_trade('sell', Decimal(str(amount)), slippage/100)
            
        except Exception as e:
            logging.error(f"Error in trading controls: {str(e)}")
            st.sidebar.error(f"Error in trading controls: {str(e)}")

    def execute_manual_trade(self, action, amount, slippage):
        """
        Execute manual trade with confirmation
        """
        try:
            if st.sidebar.button(f"Confirm {action.upper()}"):
                receipt = self.trader.execute_trade(
                    action=action,
                    token_address=self.config['tokens']['trading_token_address'],
                    amount=amount,
                    max_slippage=slippage
                )
                
                st.sidebar.success(f"Trade executed! TX: {receipt['transactionHash'].hex()}")
                
                # Update agent's state
                if action == 'buy':
                    self.agent.current_position = 'long'
                    self.agent.position_entry_price = self.cached_data['Close'].iloc[-1]
                    self.agent.current_position_size = amount
                else:
                    self.agent.current_position = None
                    self.agent.position_entry_price = None
                
                self.agent.last_trade_time = datetime.now()
                
        except Exception as e:
            logging.error(f"Error executing manual trade: {str(e)}")
            st.sidebar.error(f"Trade failed: {str(e)}")

    def run(self):
        """
        Main dashboard loop
        """
        try:
            st.title("Crypto Trading Dashboard")
            
            # Sidebar configuration
            st.sidebar.title("Dashboard Controls")
            auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
            refresh_interval = st.sidebar.slider(
                "Refresh Interval (sec)",
                min_value=30,
                max_value=300,
                value=60
            )
            
            # Manual trading controls
            self.manual_trading_controls()
            
            # Main dashboard area
            while True:
                try:
                    # Fetch latest data
                    df = self.fetch_latest_data()
                    if df is not None:
                        # Display metrics
                        self.display_trading_metrics()
                        
                        # Display charts
                        st.plotly_chart(self.create_price_chart(df))
                        st.plotly_chart(self.create_indicators_chart(df))
                        
                        # Display recent trades
                        st.header("Recent Trades")
                        st.dataframe(df.tail(10))
                    
                    # Auto refresh
                    if auto_refresh:
                        time.sleep(refresh_interval)
                        st.experimental_rerun()
                    else:
                        break
                        
                except Exception as e:
                    logging.error(f"Error in dashboard loop: {str(e)}")
                    st.error(f"Error updating dashboard: {str(e)}")
                    time.sleep(60)
                    
        except Exception as e:
            logging.error(f"Fatal dashboard error: {str(e)}")
            st.error(f"Fatal error: {str(e)}")
            raise

def main():
    """
    Run the trading dashboard
    """
    try:
        dashboard = TradingDashboard()
        dashboard.run()
        
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
        st.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main() 