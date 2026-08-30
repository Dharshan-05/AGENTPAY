'use client';
export type PaymentAttemptLogsTabType = 'ATTEMPTS' | 'RETRY_MATRIX' | 'PSP_RESPONSES' | 'LATENCY_METRICS' | '3DS_VERIFICATIONS' | 'AUDIT';
export interface PaymentAttemptLogsRecord {
  id: string;
  attemptId: string;
  paymentIntentRef: string;
  processor: string;
  attemptNumber: number;
  amount: string;
  responseCode: string;
  latencyMs: number;
  status: 'AUTHORIZED' | 'CAPTURED' | 'FAILED' | 'REQUIRES_RETRY';
}
