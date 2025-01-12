import React, { useState } from 'react';
import { Button, Select, Input, notification } from 'antd';

interface TradeControlsProps {
    token: string;
}

export const TradeControls: React.FC<TradeControlsProps> = ({ token }) => {
    const [symbol, setSymbol] = useState('');
    const [amount, setAmount] = useState('');
    const [action, setAction] = useState('buy');
    
    const executeTrade = async () => {
        try {
            const response = await fetch('/api/trade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    symbol,
                    amount: parseFloat(amount),
                    action
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                notification.success({
                    message: 'Trade Executed',
                    description: `Successfully executed ${action} trade for ${symbol}`
                });
            }
        } catch (error) {
            notification.error({
                message: 'Trade Failed',
                description: 'Failed to execute trade'
            });
        }
    };
    
    return (
        <div className="trade-controls">
            <h2>Manual Trading</h2>
            
            <Select
                value={symbol}
                onChange={setSymbol}
                placeholder="Select Symbol"
                style={{ width: '100%', marginBottom: 16 }}
            >
                <Select.Option value="BTC/USD">BTC/USD</Select.Option>
                <Select.Option value="ETH/USD">ETH/USD</Select.Option>
            </Select>
            
            <Select
                value={action}
                onChange={setAction}
                style={{ width: '100%', marginBottom: 16 }}
            >
                <Select.Option value="buy">Buy</Select.Option>
                <Select.Option value="sell">Sell</Select.Option>
            </Select>
            
            <Input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Amount"
                style={{ marginBottom: 16 }}
            />
            
            <Button
                type="primary"
                onClick={executeTrade}
                style={{ width: '100%' }}
            >
                Execute Trade
            </Button>
        </div>
    );
}; 