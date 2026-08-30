'use client';
export type SessionsTabType = 'ACTIVE' | 'OPEN' | 'PAYMENT_PENDING' | 'AUTHENTICATING' | 'COMPLETED' | 'EXPIRED' | 'AUDIT';
export interface SessionRecord {
  id: string;
  sessionId: string;
  customer: string;
  merchant: string;
  agentId: string;
  amount: string;
  ttlExpiresAt: string;
  status: 'OPEN' | 'COMPLETED' | 'EXPIRED';
}
