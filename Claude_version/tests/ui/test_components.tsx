import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TradingDashboard } from '../../frontend/src/components/TradingDashboard';
import { TradeControls } from '../../frontend/src/components/TradeControls';
import { PerformanceMetrics } from '../../frontend/src/components/PerformanceMetrics';

declare global {
    namespace NodeJS {
        interface Global {
            WebSocket: any;
            fetch: jest.Mock;
        }
    }
}

// Mock WebSocket
class MockWebSocket {
    onmessage: ((event: MessageEvent) => void) | null = null;
    close() {}
}

(global as any).WebSocket = MockWebSocket;

describe('TradingDashboard', () => {
    it('renders dashboard components', () => {
        const { getByText, getByTestId } = render(
            <TradingDashboard token="test-token" />
        );
        
        expect(getByText('AI Trading Dashboard')).toBeInTheDocument();
        expect(getByTestId('chart-container')).toBeInTheDocument();
        expect(getByTestId('controls-container')).toBeInTheDocument();
    });
    
    it('handles WebSocket updates', async () => {
        const { getByTestId } = render(
            <TradingDashboard token="test-token" />
        );
        
        // Mock WebSocket message
        const mockMessage = {
            price: 2000,
            direction: 'up',
            confidence: 0.85
        };
        
        // Simulate WebSocket message
        const ws = new WebSocket('ws://localhost:8000/ws/predictions');
        ws.onmessage({ data: JSON.stringify(mockMessage) });
        
        await waitFor(() => {
            expect(getByTestId('prediction-value')).toHaveTextContent('2000');
        });
    });
});

describe('TradeControls', () => {
    it('executes trade on form submission', async () => {
        const { getByText, getByPlaceholderText } = render(
            <TradeControls token="test-token" />
        );
        
        // Fill form
        fireEvent.change(getByPlaceholderText('Amount'), {
            target: { value: '1.0' }
        });
        
        // Mock fetch
        global.fetch = jest.fn().mockResolvedValue({
            json: () => Promise.resolve({ status: 'success' })
        });
        
        // Submit form
        fireEvent.click(getByText('Execute Trade'));
        
        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith(
                '/api/trade',
                expect.any(Object)
            );
        });
    });
    
    it('displays error notification on trade failure', async () => {
        const { getByText } = render(
            <TradeControls token="test-token" />
        );
        
        // Mock fetch failure
        global.fetch = jest.fn().mockRejectedValue(new Error('Trade failed'));
        
        fireEvent.click(getByText('Execute Trade'));
        
        await waitFor(() => {
            expect(getByText('Trade Failed')).toBeInTheDocument();
        });
    });
});

describe('PerformanceMetrics', () => {
    const mockData = {
        total_return: 0.15,
        sharpe_ratio: 1.2,
        max_drawdown: -0.05,
        win_rate: 0.65
    };
    
    it('renders performance metrics correctly', () => {
        const { getByText } = render(
            <PerformanceMetrics data={mockData} />
        );
        
        expect(getByText('15.00%')).toBeInTheDocument();
        expect(getByText('1.20')).toBeInTheDocument();
        expect(getByText('-5.00%')).toBeInTheDocument();
        expect(getByText('65.00%')).toBeInTheDocument();
    });
    
    it('handles null data gracefully', () => {
        const { container } = render(<PerformanceMetrics data={null} />);
        expect(container.firstChild).toBeNull();
    });
});

afterEach(() => {
    // Clean up WebSocket connections
    const ws = new WebSocket('ws://localhost:8000/ws/predictions');
    ws.close();
}); 