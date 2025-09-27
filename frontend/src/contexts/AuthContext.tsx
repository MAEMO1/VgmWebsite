'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/api/client';

// Types
interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'mosque_admin' | 'user';
  mosque_id?: number;
  mosque_name?: string;
  phone?: string;
  email_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (userData: RegisterData) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isMosqueAdmin: boolean;
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  mosque_id?: number;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      apiClient.setAuthToken(storedToken);
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    if (token) {
      apiClient.setAuthToken(token);
    } else {
      apiClient.clearAuthToken();
    }
  }, [token]);

  // Login function
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      
      const response = await apiClient.post<{
        token: string;
        user: User;
      }>('/api/auth/login', {
        email,
        password,
      });

      if (response.token) {
        const { token: newToken, user: userData } = response;
        
        setToken(newToken);
        setUser(userData);
        apiClient.setAuthToken(newToken);
        
        // Store in localStorage
        localStorage.setItem('auth_token', newToken);
        localStorage.setItem('auth_user', JSON.stringify(userData));
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (userData: RegisterData): Promise<boolean> => {
    try {
      setLoading(true);
      
      const response = await apiClient.post<{
        message: string;
        user_id: number;
      }>('/api/auth/register', userData);
      
      if (response.message === 'User created successfully') {
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      if (token) {
        const headers = { Authorization: `Bearer ${token}` };
        await apiClient.post('/api/auth/logout', {}, headers);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear state regardless of API call success
      setUser(null);
      setToken(null);
      apiClient.clearAuthToken();
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    }
  };

  // Computed values
  const isAuthenticated = !!user && !!token;
  const isAdmin = user?.role === 'admin';
  const isMosqueAdmin = user?.role === 'mosque_admin';

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    loading,
    isAuthenticated,
    isAdmin,
    isMosqueAdmin,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Higher-order component for protected routes
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  requiredRole?: 'admin' | 'mosque_admin'
) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, isAdmin, isMosqueAdmin, loading } = useAuth();

    if (loading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      );
    }

    if (!isAuthenticated) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Authentication Required</h1>
            <p className="text-gray-600 mb-4">Please log in to access this page.</p>
            <a href="/login" className="btn btn-primary">Go to Login</a>
          </div>
        </div>
      );
    }

    if (requiredRole === 'admin' && !isAdmin) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h1>
            <p className="text-gray-600 mb-4">You don&apos;t have permission to access this page.</p>
            <a href="/" className="btn btn-primary">Go Home</a>
          </div>
        </div>
      );
    }

    if (requiredRole === 'mosque_admin' && !isMosqueAdmin && !isAdmin) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h1>
            <p className="text-gray-600 mb-4">You don&apos;t have permission to access this page.</p>
            <a href="/" className="btn btn-primary">Go Home</a>
          </div>
        </div>
      );
    }

    return <Component {...props} />;
  };
}
