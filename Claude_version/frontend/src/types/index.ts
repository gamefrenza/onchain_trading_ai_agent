export interface WebSocketMessage {
    type: string;
    payload: any;
}

export interface TradeRequest {
    symbol: string;
    amount: number;
    type: 'buy' | 'sell';
    timestamp: string;
    nonce: number;
}

export interface PerformanceData {
    totalReturn: number;
    winRate: number;
    sharpeRatio: number;
    maxDrawdown: number;
} 