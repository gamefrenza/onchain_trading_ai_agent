import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: undefined
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        // Log to error reporting service
        console.error('Uncaught error:', error, errorInfo);
        
        // Attempt recovery
        try {
            // Close any open WebSocket connections
            const ws = new WebSocket('ws://localhost:8000/ws/predictions');
            ws.close();
            
            // Clear local storage if needed
            localStorage.removeItem('auth_token');
        } catch (e) {
            console.error('Error during recovery:', e);
        }
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="error-boundary">
                    <h2>Something went wrong</h2>
                    <details>
                        <summary>Error Details</summary>
                        <pre>{this.state.error?.toString()}</pre>
                    </details>
                    <button onClick={() => window.location.reload()}>
                        Refresh Page
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
} 