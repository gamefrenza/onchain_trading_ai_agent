import React from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { TradingDashboard } from './components/TradingDashboard';
import { useAuth } from './hooks/useAuth';

const App: React.FC = () => {
    const { token } = useAuth();
    
    return (
        <ErrorBoundary>
            <TradingDashboard token={token} />
        </ErrorBoundary>
    );
};

export default App; 