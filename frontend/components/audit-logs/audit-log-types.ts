'use client';
export type AuditLogsTabType = 'STREAM' | 'SECURITY_EVENTS' | 'FINANCIAL_POSTINGS' | 'POLICY_EVALS' | 'CHAIN_INTEGRITY' | 'EXPORTS' | 'AUDIT';
export interface AuditLogRecord {
  id: string;
  logId: string;
  actor: string;
  action: string;
  resourceId: string;
  ipAddress: string;
  timestamp: string;
  sha256Hash: string;
  integrity: 'VERIFIED' | 'TAMPER_EVIDENT';
}
