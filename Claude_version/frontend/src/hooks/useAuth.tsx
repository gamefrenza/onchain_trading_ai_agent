import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (credentials: { email: string; password: string }) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    
    // Add token expiration check
    const isTokenValid = (token: string): boolean => {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp * 1000 > Date.now();
        } catch {
            return false;
        }
    };

    useEffect(() => {
        const storedToken = localStorage.getItem('auth_token');
        if (storedToken && isTokenValid(storedToken)) {
            setToken(storedToken);
            fetchUserData(storedToken);
        } else {
            localStorage.removeItem('auth_token');
        }
    }, []);
    
    const login = async (credentials: { email: string; password: string }) => {
        try {
            // Add request timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);

            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'  // CSRF protection
                },
                credentials: 'same-origin',  // Include cookies
                signal: controller.signal,
                body: JSON.stringify(credentials)
            });

            clearTimeout(timeoutId);
            
            if (!response.ok) throw new Error('Login failed');
            
            const data = await response.json();
            setToken(data.token);
            setUser(data.user);
            localStorage.setItem('auth_token', data.token);
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    };
    
    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('auth_token');
    };
    
    return (
        <AuthContext.Provider value={{ user, token, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 