'use client';
export type ChargebacksTabType = 'DISPUTES' | 'EVIDENCE_SUBMISSION' | 'WON_DISPUTES' | 'LOST_DISPUTES' | 'PREVENTATIVE_ALERTS' | 'AUDIT';
export interface ChargebackRecord {
  id: string;
  disputeId: string;
  txnRef: string;
  agentRef: string;
  disputeAmount: string;
  reasonCode: string;
  evidenceDueDate: string;
  status: 'UNDER_REVIEW' | 'EVIDENCE_SUBMITTED' | 'WON' | 'LOST';
}
