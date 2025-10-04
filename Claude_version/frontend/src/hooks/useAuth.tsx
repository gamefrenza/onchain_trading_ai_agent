import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { apiClient } from '../api/client';

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (credentials: { email: string; password: string }) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

// fetchUserData must be inside the provider to access setUser/setToken

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    
    const fetchUserData = async (jwtToken: string): Promise<void> => {
        try {
            const userResp = await apiClient.fetch<User>('/api/v1/user/me', {
                headers: {
                    Authorization: `Bearer ${jwtToken}`
                }
            });
            setUser(userResp);
        } catch (error) {
            console.error('Error fetching user data:', error);
            localStorage.removeItem('auth_token');
            setToken(null);
            setUser(null);
        }
    };
    
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

            // Backend exposes OAuth2 token at /api/v1/token
            const response = await fetch('/api/v1/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                signal: controller.signal,
                body: new URLSearchParams({
                    username: credentials.email,
                    password: credentials.password
                }) as any
            });

            clearTimeout(timeoutId);
            
            if (!response.ok) throw new Error('Login failed');
            
            const data = await response.json();
            // FastAPI returns access_token
            const accessToken: string = data.access_token;
            setToken(accessToken);
            localStorage.setItem('auth_token', accessToken);
            await fetchUserData(accessToken);
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