'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api-client';
import { PolicyResponse, PolicyCreateRequest, PolicyListResponse } from '../types/api';

export function usePolicies() {
  const [policies, setPolicies] = useState<PolicyResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPolicies = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<PolicyListResponse>('/policies');
      setPolicies(res.items || []);
    } catch (err: any) {
      console.warn('Failed to fetch policies from backend:', err.message);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPolicies();
  }, [fetchPolicies]);

  const createPolicy = async (data: PolicyCreateRequest): Promise<PolicyResponse> => {
    setIsLoading(true);
    try {
      const newPolicy = await apiClient.post<PolicyResponse>('/policies', data);
      setPolicies((prev) => [newPolicy, ...prev]);
      return newPolicy;
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const activatePolicy = async (policyId: string) => {
    try {
      const res = await apiClient.post<PolicyResponse>(`/policies/${policyId}/activate`);
      setPolicies((prev) =>
        prev.map((p) => (p.id === policyId ? { ...p, status: 'ACTIVE' } : p))
      );
      return res;
    } catch (err: any) {
      throw err;
    }
  };

  const deactivatePolicy = async (policyId: string) => {
    try {
      const res = await apiClient.post<PolicyResponse>(`/policies/${policyId}/deactivate`);
      setPolicies((prev) =>
        prev.map((p) => (p.id === policyId ? { ...p, status: 'DISABLED' } : p))
      );
      return res;
    } catch (err: any) {
      throw err;
    }
  };

  return {
    policies,
    isLoading,
    error,
    refetch: fetchPolicies,
    createPolicy,
    activatePolicy,
    deactivatePolicy,
  };
}
