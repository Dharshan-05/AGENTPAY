export type ReconciliationTabType =
  | 'SETTLEMENTS'
  | 'DISPUTES'
  | 'DISCREPANCIES'
  | 'BATCH_MATCHING'
  | 'AUDIT_TRAIL';

export interface SourceSettlementBatch {
  id: string;
  processor: string;
  grossAmount: string;
  feeAmount: string;
  netAmount: string;
  matchedCount: number;
  unmatchedCount: number;
  status: 'MATCHED' | 'DISCREPANCY' | 'PENDING_CLEARING';
  settlementDate: string;
}

export interface SourceDisputeRecord {
  id: string;
  disputeId: string;
  transactionId: string;
  agentId: string;
  merchant: string;
  amount: string;
  reason: 'AGENT_UNAUTHORIZED' | 'FRAUD_SUSPECTED' | 'DUPLICATE_CHARGE' | 'POLICY_VIOLATION';
  status: 'OPEN' | 'UNDER_REVIEW' | 'EVIDENCE_SUBMITTED' | 'WON' | 'LOST';
  evidenceDeadline: string;
  disputeDate: string;
}

export interface SourceDiscrepancyRecord {
  id: string;
  batchId: string;
  transactionId: string;
  agentId: string;
  expectedAmount: string;
  settledAmount: string;
  varianceAmount: string;
  varianceType: 'FEE_MISMATCH' | 'UNMATCHED_SETTLEMENT' | 'OVER_AUTHORIZATION' | 'CURRENCY_SLIPPAGE';
  status: 'UNRESOLVED' | 'RESOLVED' | 'WRITTEN_OFF';
  timestamp: string;
}

export interface SourceAuditLedgerEntry {
  id: string;
  eventId: string;
  actor: string;
  action: string;
  amount: string;
  status: 'SUCCESS' | 'FAILED';
  timestamp: string;
  hash: string;
}
