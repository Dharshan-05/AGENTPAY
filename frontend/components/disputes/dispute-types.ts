'use client';

export type DisputeTabType = 'REGISTRY' | 'OPEN' | 'EVIDENCE' | 'CHARGEBACKS' | 'RESPONSES' | 'RESOLUTION' | 'RISK' | 'AUDIT';

export interface DisputeRecord {
  id: string;
  disputeId: string;
  transactionId: string;
  customer: string;
  merchant: string;
  amount: string;
  currency: string;
  reason: string;
  network: string;
  deadline: string;
  riskScore: number;
  status: 'NEEDS_RESPONSE' | 'UNDER_REVIEW' | 'WON' | 'LOST';
}
