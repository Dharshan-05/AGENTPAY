'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api-client';
import { AgentResponse, AgentCreateRequest, AgentListResponse } from '../types/api';

export function useAgents() {
  const [agents, setAgents] = useState<AgentResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<AgentListResponse>('/agents');
      setAgents(res.agents || []);
    } catch (err: any) {
      console.warn('Failed to fetch agents from backend, keeping cached/local state:', err.message);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  const createAgent = async (data: AgentCreateRequest): Promise<AgentResponse> => {
    setIsLoading(true);
    try {
      const newAgent = await apiClient.post<AgentResponse>('/agents', data);
      setAgents((prev) => [newAgent, ...prev]);
      return newAgent;
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const activateAgent = async (agentId: string, reason: string = 'User activation') => {
    try {
      const res = await apiClient.post(`/agents/${agentId}/activate`, { reason });
      setAgents((prev) =>
        prev.map((a) => (a.id === agentId ? { ...a, status: 'ACTIVE' } : a))
      );
      return res;
    } catch (err: any) {
      throw err;
    }
  };

  const suspendAgent = async (agentId: string, reason: string = 'User suspension') => {
    try {
      const res = await apiClient.post(`/agents/${agentId}/suspend`, { reason });
      setAgents((prev) =>
        prev.map((a) => (a.id === agentId ? { ...a, status: 'SUSPENDED' } : a))
      );
      return res;
    } catch (err: any) {
      throw err;
    }
  };

  return {
    agents,
    isLoading,
    error,
    refetch: fetchAgents,
    createAgent,
    activateAgent,
    suspendAgent,
  };
}
