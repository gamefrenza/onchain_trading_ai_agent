import React, { useEffect, useState } from 'react';
import { ethers } from 'ethers';
import './App.css';

interface TradingState {
  isActive: boolean;
  lastTrade: string;
  balance: string;
}

function App() {
  const [tradingState, setTradingState] = useState<TradingState>({
    isActive: false,
    lastTrade: '',
    balance: '0',
  });

  useEffect(() => {
    // Connect to the trading engine and fetch initial state
    const fetchTradingState = async () => {
      try {
        // Implement connection to backend
      } catch (error) {
        console.error('Failed to fetch trading state:', error);
      }
    };

    fetchTradingState();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Trading Agent Dashboard</h1>
      </header>
      <main>
        <div className="trading-status">
          <h2>Trading Status</h2>
          <p>Active: {tradingState.isActive ? 'Yes' : 'No'}</p>
          <p>Last Trade: {tradingState.lastTrade}</p>
          <p>Current Balance: {tradingState.balance} ETH</p>
        </div>
      </main>
    </div>
  );
}

export default App; 