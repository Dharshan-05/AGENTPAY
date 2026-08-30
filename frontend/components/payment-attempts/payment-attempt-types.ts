'use client';
export type AttemptsTabType = 'TELEMETRY' | 'AUTHORIZED' | 'CAPTURED' | 'FAILED_RETRIES' | 'RESPONSE_CODES' | 'CONNECTOR_SPLIT' | 'AUDIT';
export interface AttemptRecord {
  id: string;
  attemptId: string;
  paymentIntentId: string;
  orderId: string;
  processor: string;
  attemptNumber: number;
  amount: string;
  latencyMs: number;
  responseCode: string;
  status: 'AUTHORIZED' | 'CAPTURED' | 'FAILED' | 'RETRYING';
}
