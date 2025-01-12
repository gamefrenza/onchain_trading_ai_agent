import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTabWidget, 
                            QTableWidget, QTableWidgetItem, QLineEdit, 
                            QComboBox, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPalette, QColor
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
from trading_strategy import TradingStrategy
from trade_executor import TradeExecutor
from quant_analysis import QuantAnalyzer
import asyncio
import qasync

class AsyncUpdateThread(QThread):
    """Thread for async data updates"""
    update_signal = pyqtSignal(dict)
    
    def __init__(self, fetcher, analyzer):
        super().__init__()
        self.fetcher = fetcher
        self.analyzer = analyzer
        self.running = True
        
    async def fetch_data(self):
        while self.running:
            try:
                # Fetch and analyze market data
                trades = await self.fetcher.get_dex_trades(pair='ETH/USDT', limit=100)
                df = self.analyzer.prepare_data(pd.DataFrame(trades))
                df = self.analyzer.add_technical_indicators(df)
                
                self.update_signal.emit({
                    'market_data': df,
                    'timestamp': datetime.now()
                })
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Error fetching data: {e}")
                await asyncio.sleep(5)
    
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.fetch_data())
    
    def stop(self):
        self.running = False

class TradingDashboard(QMainWindow):
    def __init__(self, strategy: TradingStrategy, executor: TradeExecutor):
        super().__init__()
        self.strategy = strategy
        self.executor = executor
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('AI Trading Dashboard')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Add different views
        tabs.addTab(MarketView(self.strategy), "Market Data")
        tabs.addTab(TradesView(self.executor), "Active Trades")
        tabs.addTab(PerformanceView(), "Performance")
        tabs.addTab(ControlPanel(self.strategy, self.executor), "Control Panel")
        
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('System Ready')

class MarketView(QWidget):
    def __init__(self, strategy):
        super().__init__()
        self.strategy = strategy
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Price chart
        self.chart_widget = QWidget()
        layout.addWidget(self.chart_widget)
        
        # Market data table
        self.market_table = QTableWidget()
        self.market_table.setColumnCount(6)
        self.market_table.setHorizontalHeaderLabels([
            'Time', 'Price', 'Volume', 'RSI', 'MACD', 'Signal'
        ])
        layout.addWidget(self.market_table)
        
    def update_chart(self, df: pd.DataFrame):
        # Create plotly figure
        fig = make_subplots(rows=2, cols=1, shared_xaxis=True,
                           vertical_spacing=0.03, subplot_titles=('Price', 'Volume'),
                           row_heights=[0.7, 0.3])
        
        fig.add_trace(go.Candlestick(
            x=df['timestamp'],
            open=df['price'],
            high=df['price'],
            low=df['price'],
            close=df['price'],
            name='Price'
        ), row=1, col=1)
        
        fig.add_trace(go.Bar(
            x=df['timestamp'],
            y=df['volume'],
            name='Volume'
        ), row=2, col=1)
        
        # Update chart widget (you'll need to implement a custom plotly widget)
        # self.chart_widget.update_figure(fig)
        
    def update_market_table(self, df: pd.DataFrame):
        self.market_table.setRowCount(len(df))
        for i, row in df.iterrows():
            self.market_table.setItem(i, 0, QTableWidgetItem(str(row['timestamp'])))
            self.market_table.setItem(i, 1, QTableWidgetItem(f"${row['price']:.2f}"))
            self.market_table.setItem(i, 2, QTableWidgetItem(f"{row['volume']:.2f}"))
            self.market_table.setItem(i, 3, QTableWidgetItem(f"{row['rsi']:.2f}"))
            self.market_table.setItem(i, 4, QTableWidgetItem(f"{row['macd']:.2f}"))
            
            # Add signal indicator if available
            signal = self.strategy.generate_trade_signals(df.iloc[i:i+1])
            if signal:
                self.market_table.setItem(i, 5, QTableWidgetItem(signal[0].signal_type))

class TradesView(QWidget):
    def __init__(self, executor):
        super().__init__()
        self.executor = executor
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Active trades table
        self.trades_table = QTableWidget()
        self.trades_table.setColumnCount(7)
        self.trades_table.setHorizontalHeaderLabels([
            'Entry Time', 'Type', 'Entry Price', 'Current Price', 
            'Size', 'PnL', 'Status'
        ])
        layout.addWidget(self.trades_table)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.close_button = QPushButton('Close Selected')
        self.close_button.clicked.connect(self.close_selected_trade)
        controls_layout.addWidget(self.close_button)
        
        layout.addLayout(controls_layout)
        
    def update_trades(self):
        self.trades_table.setRowCount(len(self.executor.current_positions))
        for i, position in enumerate(self.executor.current_positions):
            self.trades_table.setItem(i, 0, QTableWidgetItem(str(position.entry_time)))
            self.trades_table.setItem(i, 1, QTableWidgetItem(position.position_type.value))
            self.trades_table.setItem(i, 2, QTableWidgetItem(f"${position.entry_price:.2f}"))
            # Add other position details
            
    async def close_selected_trade(self):
        selected_rows = self.trades_table.selectedItems()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        position = self.executor.current_positions[row]
        # Implement position closing logic

class PerformanceView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QGridLayout(self)
        
        # Performance metrics
        metrics_frame = QFrame()
        metrics_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        metrics_layout = QGridLayout(metrics_frame)
        
        metrics = [
            ('Total Return', '0.00%'),
            ('Win Rate', '0.00%'),
            ('Sharpe Ratio', '0.00'),
            ('Max Drawdown', '0.00%'),
            ('Total Trades', '0'),
            ('Active Trades', '0')
        ]
        
        for i, (label, value) in enumerate(metrics):
            metrics_layout.addWidget(QLabel(label), i // 2, (i % 2) * 2)
            metrics_layout.addWidget(QLabel(value), i // 2, (i % 2) * 2 + 1)
            
        layout.addWidget(metrics_frame, 0, 0)
        
        # Performance chart
        self.chart_widget = QWidget()
        layout.addWidget(self.chart_widget, 1, 0)
        
    def update_metrics(self, performance_data: dict):
        # Update performance metrics and chart
        pass

class ControlPanel(QWidget):
    def __init__(self, strategy, executor):
        super().__init__()
        self.strategy = strategy
        self.executor = executor
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Strategy controls
        strategy_group = QFrame()
        strategy_group.setFrameStyle(QFrame.Box | QFrame.Raised)
        strategy_layout = QGridLayout(strategy_group)
        
        strategy_layout.addWidget(QLabel('Risk Per Trade:'), 0, 0)
        self.risk_input = QLineEdit()
        strategy_layout.addWidget(self.risk_input, 0, 1)
        
        strategy_layout.addWidget(QLabel('Min Confidence:'), 1, 0)
        self.confidence_input = QLineEdit()
        strategy_layout.addWidget(self.confidence_input, 1, 1)
        
        layout.addWidget(strategy_group)
        
        # Manual trade controls
        trade_group = QFrame()
        trade_group.setFrameStyle(QFrame.Box | QFrame.Raised)
        trade_layout = QGridLayout(trade_group)
        
        trade_layout.addWidget(QLabel('Token Pair:'), 0, 0)
        self.pair_combo = QComboBox()
        self.pair_combo.addItems(['ETH/USDT', 'BTC/USDT'])
        trade_layout.addWidget(self.pair_combo, 0, 1)
        
        trade_layout.addWidget(QLabel('Amount:'), 1, 0)
        self.amount_input = QLineEdit()
        trade_layout.addWidget(self.amount_input, 1, 1)
        
        self.buy_button = QPushButton('Buy')
        self.buy_button.clicked.connect(self.execute_manual_trade)
        trade_layout.addWidget(self.buy_button, 2, 0)
        
        self.sell_button = QPushButton('Sell')
        self.sell_button.clicked.connect(self.execute_manual_trade)
        trade_layout.addWidget(self.sell_button, 2, 1)
        
        layout.addWidget(trade_group)
        
        # System controls
        system_group = QFrame()
        system_group.setFrameStyle(QFrame.Box | QFrame.Raised)
        system_layout = QHBoxLayout(system_group)
        
        self.start_button = QPushButton('Start Trading')
        self.start_button.clicked.connect(self.toggle_trading)
        system_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton('Emergency Stop')
        self.stop_button.clicked.connect(self.emergency_stop)
        self.stop_button.setStyleSheet('background-color: red; color: white;')
        system_layout.addWidget(self.stop_button)
        
        layout.addWidget(system_group)
        
    async def execute_manual_trade(self):
        # Implement manual trade execution
        pass
        
    def toggle_trading(self):
        # Implement trading start/stop
        pass
        
    async def emergency_stop(self):
        # Implement emergency stop
        pass

def main():
    app = QApplication(sys.argv)
    
    # Initialize components
    strategy = TradingStrategy(QuantAnalyzer())
    executor = TradeExecutor(
        web3_provider=os.getenv('ETH_NODE_URL'),
        private_key=os.getenv('PRIVATE_KEY'),
        dex_router_address=os.getenv('DEX_ROUTER_ADDRESS')
    )
    
    # Create and show the dashboard
    dashboard = TradingDashboard(strategy, executor)
    dashboard.show()
    
    # Start the async event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Start the update thread
    update_thread = AsyncUpdateThread(strategy.quant_analyzer.blockchain_fetcher, 
                                    strategy.quant_analyzer)
    update_thread.update_signal.connect(dashboard.update_data)
    update_thread.start()
    
    # Run the application
    with loop:
        loop.run_forever()

if __name__ == '__main__':
    main() 