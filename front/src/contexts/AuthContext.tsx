import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthContextType, RegisterData } from '../types';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored user session
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // Mock API call - replace with actual FastAPI endpoint
      const response = await mockApiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      
      const userData = response.user;
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      throw new Error('Login failed');
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: RegisterData) => {
    setLoading(true);
    try {
      // Mock API call - replace with actual FastAPI endpoint
      const response = await mockApiCall('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      });
      
      const newUser = response.user;
      setUser(newUser);
      localStorage.setItem('user', JSON.stringify(newUser));
    } catch (error) {
      throw new Error('Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Mock API function - replace with actual API calls
const mockApiCall = async (endpoint: string, options: RequestInit) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  if (endpoint === '/auth/login') {
    return {
      user: {
        id: '1',
        email: 'user@example.com',
        name: 'John Doe',
        timezone: 'UTC',
        gender: 'male',
        createdAt: new Date(),
      }
    };
  }
  
  if (endpoint === '/auth/register') {
    const userData = JSON.parse(options.body as string);
    return {
      user: {
        id: Math.random().toString(36).substr(2, 9),
        ...userData,
        createdAt: new Date(),
      }
    };
  }
  
  throw new Error('Endpoint not found');
};