import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { User, RegisterData } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const API_URL = 'http://localhost:8000/api';

let refreshTimeout: ReturnType<typeof setTimeout>;

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  const setTokens = (accessToken: string, refreshToken: string) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    setupRefreshToken();
  };

  const setupRefreshToken = () => {
    if (refreshTimeout) clearTimeout(refreshTimeout);

    // Refresh 1 minute before token expires
    refreshTimeout = setTimeout(refreshAccessToken, 29 * 60 * 1000);
  };

  const refreshAccessToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        setUser(null);
        return;
      }

      const response = await axios.post(`${API_URL}/auth/refresh`, {
        refresh_token: refreshToken,
      });

      const { access_token, refresh_token } = response.data;
      setTokens(access_token, refresh_token);
    } catch (error) {
      console.error('Failed to refresh token:', error);
      logout();
    }
  };

  const fetchUser = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) return;

      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(response.data);
      setupRefreshToken();
    } catch (error) {
      console.error('Failed to fetch user:', error);
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        await refreshAccessToken();
        await fetchUser();
      }
    }
  };

  useEffect(() => {
    fetchUser();
    return () => {
      if (refreshTimeout) clearTimeout(refreshTimeout);
    };
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${API_URL}/auth/token`,
        new URLSearchParams({
          username: email,
          password: password,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      const { access_token, refresh_token } = response.data;
      setTokens(access_token, refresh_token);
      await fetchUser();
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: RegisterData) => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/auth/register`, data);
      await login(data.email, data.password);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    if (refreshTimeout) clearTimeout(refreshTimeout);
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
