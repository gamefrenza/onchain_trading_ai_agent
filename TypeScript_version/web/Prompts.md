1. For the Initial Project Setup:
```
Create a Python project for an onchain AI trading agent with the following requirements:
- Use Web3.py for blockchain interaction
- Implement async functionality for real-time monitoring
- Set up TensorFlow for AI model implementation
- Include FastAPI for the web interface
- Implement proper logging and error handling
- Set up environment configuration management
Please include all necessary package dependencies and create a proper project structure.
```

2. For the Blockchain Monitoring Component:
```
Implement a blockchain event listener with these features:
- Monitor DEX smart contracts for trading events
- Parse and store trade data in a structured format
- Handle multiple trading pairs simultaneously
- Implement WebSocket connections for real-time updates
- Include error handling for network issues
- Add retry mechanisms for failed connections
Please provide example code for event filtering and processing.
```

3. For the AI/ML Component:
```
Create a machine learning module that:
- Processes historical trading data
- Implements technical indicators (RSI, MACD, etc.)
- Creates a deep learning model for pattern recognition
- Includes backtesting capabilities
- Has proper model validation
- Implements risk management features
Include example code for model training and prediction.
```

4. For the Trading Strategy Component:
```
Develop a trading strategy module that:
- Analyzes patterns from the AI model
- Implements various trading strategies
- Includes risk management rules
- Has position sizing logic
- Implements stop-loss mechanisms
- Provides strategy performance metrics
Show example implementation of strategy execution.
```

5. For the Web Interface:
```
Create a FastAPI-based web interface that:
- Displays real-time trading activities
- Shows AI model predictions
- Provides manual trading controls
- Displays performance metrics
- Implements authentication
- Includes WebSocket for real-time updates
Include React components for the frontend.
```

For the Frontend UI, let me provide a React component structure:

```tsx
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { AlertCircle, TrendingUp, Activity, DollarSign } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

const TradingDashboard = () => {
  const [performance, setPerformance] = useState([]);
  const [activePositions, setActivePositions] = useState([]);
  const [aiPredictions, setAiPredictions] = useState({});
  
  return (
    <div className="p-6 space-y-6">
      {/* Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <DollarSign className="mr-2" />
              Portfolio Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$124,532.00</div>
            <div className="text-green-500">+2.4%</div>
          </CardContent>
        </Card>
        
        {/* Active Positions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="mr-2" />
              Active Trades
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <div className="text-sm text-gray-500">Currently Open</div>
          </CardContent>
        </Card>
        
        {/* AI Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="mr-2" />
              AI Predictions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Bullish pattern detected in ETH/USDT
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
      
      {/* Performance Chart */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Performance History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px]">
            <LineChart
              width={800}
              height={400}
              data={performance}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" />
            </LineChart>
          </div>
        </CardContent>
      </Card>
      
      {/* Trading Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Manual Trading Controls</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <button className="w-full p-2 bg-red-500 text-white rounded">
                Emergency Stop
              </button>
              <button className="w-full p-2 bg-green-500 text-white rounded">
                Resume Trading
              </button>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Risk Parameters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Max Position Size</span>
                <span>$10,000</span>
              </div>
              <div className="flex justify-between">
                <span>Stop Loss</span>
                <span>2%</span>
              </div>
              <div className="flex justify-between">
                <span>Take Profit</span>
                <span>5%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TradingDashboard;

```

Additional guidance for Cursor IDE:

1. For error handling, prompt Cursor to:
```
Add comprehensive error handling for:
- Network disconnections
- Smart contract failures
- API timeouts
- Invalid trading parameters
- Model prediction errors
```

2. For testing, prompt Cursor to:
```
Create test cases for:
- Unit tests for each component
- Integration tests for the complete system
- Mock blockchain responses
- AI model validation
- UI component testing
```

3. For deployment, prompt Cursor to:
```
Set up deployment configuration for:
- Docker containerization
- Environment variable management
- Database setup
- Model serving
- Frontend hosting
```