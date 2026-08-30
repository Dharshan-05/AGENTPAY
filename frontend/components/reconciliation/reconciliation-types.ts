export type ReconciliationTabType =
  | 'SETTLEMENTS'
  | 'DISPUTES'
  | 'DISCREPANCIES'
  | 'AUDIT';

export interface SettlementBatchRecord {
  id: string;
  processor: string;
  settlementDate: string;
  currency: string;
  grossAmount: string;
  fees: string;
  netAmount: string;
  matchedCount: number;
  unmatchedCount: number;
  status: 'MATCHED' | 'PARTIAL MATCH' | 'VARIANCE' | 'REVIEW' | 'FAILED';
  auditHash: string;
}

export interface DisputeRecord {
  id: string;
  disputeId: string;
  transactionId: string;
  agentId: string;
  merchant: string;
  amount: string;
  reason: 'AGENT_UNAUTHORIZED' | 'POLICY_VIOLATION' | 'DUPLICATE_TRANSACTION' | 'AMOUNT_MISMATCH' | 'FRAUD_SUSPECTED' | 'SERVICE_NOT_RECEIVED';
  deadline: string;
  status: 'OPENED' | 'UNDER REVIEW' | 'EVIDENCE PREPARING' | 'EVIDENCE SUBMITTED' | 'WON' | 'LOST';
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  createdDate: string;
}

export interface DiscrepancyRecord {
  id: string;
  varianceId: string;
  transactionId: string;
  agentId: string;
  processor: string;
  expectedAmount: string;
  actualAmount: string;
  deltaAmount: string;
  type: 'FEE_MISMATCH' | 'OVER_AUTHORIZATION' | 'UNDER_SETTLEMENT' | 'UNMATCHED_CLEARING' | 'DUPLICATE_CAPTURE';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED';
  recommendation: string;
}

export interface ReconciliationAuditEvent {
  id: string;
  eventId: string;
  timestamp: string;
  actor: string;
  entity: string;
  action: string;
  source: string;
  hash: string;
  prevHash: string;
  status: 'VERIFIED' | 'INVALID';
}
