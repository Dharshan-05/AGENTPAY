'use client';
export type CommissionsTabType = 'COMMISSIONS' | 'AGENTS' | 'REVENUE_SPLITS' | 'TIERS' | 'PAYOUT_SCHEDULE' | 'AUDIT';
export interface CommissionRecord {
  id: string;
  commissionId: string;
  agentId: string;
  agentName: string;
  commissionAmount: string;
  rate: string;
  status: 'PAID' | 'PENDING';
}
