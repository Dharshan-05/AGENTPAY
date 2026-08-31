'use client';

import { useState } from 'react';
import { apiClient } from '../api-client';
import {
  FraudGuardInferenceRequest,
  FraudGuardInferenceResponse,
  RiskDecisionEvaluateRequest,
  RiskDecisionEvaluateResponse,
} from '../types/api';

export function useFraudGuard() {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const runInference = async (req: FraudGuardInferenceRequest): Promise<FraudGuardInferenceResponse> => {
    setIsLoading(true);
    setError(null);
    try {
      return await apiClient.post<FraudGuardInferenceResponse>('/fraudguard/inference', req);
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const evaluateRiskDecision = async (req: RiskDecisionEvaluateRequest): Promise<RiskDecisionEvaluateResponse> => {
    setIsLoading(true);
    setError(null);
    try {
      // Try /risk-decisions/evaluate first, fallback to /fraudguard/evaluate if needed
      try {
        return await apiClient.post<RiskDecisionEvaluateResponse>('/risk-decisions/evaluate', req);
      } catch {
        return await apiClient.post<RiskDecisionEvaluateResponse>('/fraudguard/evaluate', req);
      }
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const getLocalXAI = async (transactionId: string) => {
    setIsLoading(true);
    try {
      return await apiClient.post('/fraudguard/xai/local-explanation', { transaction_id: transactionId });
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const getGlobalXAI = async () => {
    setIsLoading(true);
    try {
      return await apiClient.post('/fraudguard/xai/global-explanation', {});
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
    runInference,
    evaluateRiskDecision,
    getLocalXAI,
    getGlobalXAI,
  };
}
