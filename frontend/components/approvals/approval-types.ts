'use client';

export type ApprovalsTabType = 'QUEUE' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'ESCALATED' | 'POLICIES' | 'SLA' | 'AUDIT';

export interface ApprovalRecord {
  id: string;
  approvalId: string;
  transactionId: string;
  agentId: string;
  policyId: string;
  amount: string;
  riskScore: number;
  requester: string;
  approver: string;
  slaRemaining: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'ESCALATED';
  created: string;
}
