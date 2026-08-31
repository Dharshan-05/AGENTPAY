'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient, ApiClientError } from '../api-client';
import { UserLoginRequest, UserLoginResponseData, UserMeResponseData } from '../types/api';

export function useAuth() {
  const [user, setUser] = useState<UserMeResponseData | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCurrentUser = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const storedToken = localStorage.getItem('agentpay_token');
      if (!storedToken) {
        setUser(null);
        setToken(null);
        setIsLoading(false);
        return null;
      }
      setToken(storedToken);
      const userData = await apiClient.get<UserMeResponseData>('/auth/me');
      setUser(userData);
      return userData;
    } catch (err: any) {
      console.warn('Auth check failed or session expired:', err);
      localStorage.removeItem('agentpay_token');
      localStorage.removeItem('agentpay_refresh_token');
      localStorage.removeItem('agentpay_authenticated');
      setUser(null);
      setToken(null);
      setError(err.message || 'Session expired.');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  const login = async (credentials: UserLoginRequest): Promise<UserLoginResponseData> => {
    setIsLoading(true);
    setError(null);
    try {
      const authData = await apiClient.post<UserLoginResponseData>('/auth/login', credentials, { skipAuth: true });
      if (authData.access_token) {
        localStorage.setItem('agentpay_token', authData.access_token);
        if (authData.refresh_token) {
          localStorage.setItem('agentpay_refresh_token', authData.refresh_token);
        }
        localStorage.setItem('agentpay_authenticated', 'true');
        setToken(authData.access_token);
        await fetchCurrentUser();
      }
      return authData;
    } catch (err: any) {
      const msg = err.message || 'Failed to authenticate.';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiClient.post('/auth/logout');
    } catch (err) {
      console.warn('Logout endpoint notification failed:', err);
    } finally {
      localStorage.removeItem('agentpay_token');
      localStorage.removeItem('agentpay_refresh_token');
      localStorage.removeItem('agentpay_authenticated');
      localStorage.removeItem('agentpay_user');
      setUser(null);
      setToken(null);
    }
  };

  return {
    user,
    token,
    isAuthenticated: !!token,
    isLoading,
    error,
    login,
    logout,
    refreshUser: fetchCurrentUser,
  };
}
