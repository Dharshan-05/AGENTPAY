'use client';

import { useState } from 'react';
import { apiClient } from '../api-client';
import {
  PurchaseRequestCreateRequest,
  PurchaseRequestResponse,
  CommerceExecutionResponse,
} from '../types/api';

export function useTransactions() {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const createPurchaseRequest = async (req: PurchaseRequestCreateRequest): Promise<PurchaseRequestResponse> => {
    setIsLoading(true);
    setError(null);
    try {
      return await apiClient.post<PurchaseRequestResponse>('/purchase-requests', req);
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const getPurchaseRequest = async (requestId: string): Promise<PurchaseRequestResponse> => {
    setIsLoading(true);
    try {
      return await apiClient.get<PurchaseRequestResponse>(`/purchase-requests/${requestId}`);
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const validatePurchaseRequest = async (requestId: string) => {
    setIsLoading(true);
    try {
      return await apiClient.post(`/purchase-requests/${requestId}/validate`, {});
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const executePurchaseRequest = async (requestId: string, idempotencyKey?: string): Promise<CommerceExecutionResponse> => {
    setIsLoading(true);
    try {
      return await apiClient.post<CommerceExecutionResponse>(`/purchase-requests/${requestId}/execute`, {
        idempotency_key: idempotencyKey,
      });
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const cancelPurchaseRequest = async (requestId: string): Promise<CommerceExecutionResponse> => {
    setIsLoading(true);
    try {
      return await apiClient.post<CommerceExecutionResponse>(`/purchase-requests/${requestId}/cancel`, {});
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    createPurchaseRequest,
    getPurchaseRequest,
    validatePurchaseRequest,
    executePurchaseRequest,
    cancelPurchaseRequest,
  };
}
