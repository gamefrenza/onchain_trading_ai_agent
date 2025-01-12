import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { TradeRequest } from '../types';

interface TradeControlsProps {
    onTrade: (trade: TradeRequest) => Promise<void>;
    availableBalance: number;
}

export const TradeControls: React.FC<TradeControlsProps> = ({
    onTrade,
    availableBalance
}) => {
    const [amount, setAmount] = useState<string>('');
    const [pair, setPair] = useState<string>('');
    const [type, setType] = useState<'buy' | 'sell'>('buy');
    const { token } = useAuth();
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    
    const validateAmount = (value: string): boolean => {
        const num = parseFloat(value);
        return !isNaN(num) && num > 0 && num <= availableBalance;
    };
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!validateAmount(amount) || !pair) {
            console.error('Invalid trade parameters');
            return;
        }

        if (isSubmitting) return;
        setIsSubmitting(true);

        if (parseFloat(amount) > availableBalance * 0.1) {
            const confirmed = window.confirm('This is a large trade. Are you sure?');
            if (!confirmed) return;
        }

        try {
            await onTrade({
                type,
                pair,
                amount: parseFloat(amount),
                timestamp: new Date().toISOString(),
                nonce: Date.now()
            });
            // Reset form
            setAmount('');
        } catch (error) {
            console.error('Trade execution failed:', error);
        }
    };
    
    return (
        <div className="trade-controls">
            <h3>Manual Trading</h3>
            <div className="available-balance">
                Available: ${availableBalance.toFixed(2)}
            </div>
            <form onSubmit={handleSubmit}>
                <select value={pair} onChange={(e) => setPair(e.target.value)}>
                    <option value="">Select Pair</option>
                    <option value="ETH/USDT">ETH/USDT</option>
                    <option value="BTC/USDT">BTC/USDT</option>
                </select>
                
                <div className="trade-type-buttons">
                    <button
                        type="button"
                        className={type === 'buy' ? 'active' : ''}
                        onClick={() => setType('buy')}
                    >
                        Buy
                    </button>
                    <button
                        type="button"
                        className={type === 'sell' ? 'active' : ''}
                        onClick={() => setType('sell')}
                    >
                        Sell
                    </button>
                </div>
                
                <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="Amount"
                    min="0"
                    step="0.01"
                />
                
                <button type="submit" disabled={!amount || !pair}>
                    Execute Trade
                </button>
            </form>
        </div>
    );
}; 