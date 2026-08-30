'use client';
export type CheckoutTabType = 'SESSIONS' | 'ACTIVE' | '3DS_CHALLENGE' | 'COMPLETED' | 'FAILED' | 'ROUTING' | 'AUDIT';
export interface CheckoutSessionRecord {
  id: string;
  sessionId: string;
  agentId: string;
  merchant: string;
  amount: string;
  threeDsStatus: 'AUTHENTICATED' | 'CHALLENGE_REQUIRED' | 'PASSED';
  processor: string;
  status: 'COMPLETED' | 'PROCESSING' | 'FAILED';
}
