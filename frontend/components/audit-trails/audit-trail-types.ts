'use client';
export type AuditTrailsTabType = 'EVENT_LOGS' | 'HASH_CHAINS' | 'SECURITY_ACTORS' | 'TAMPER_CHECK' | 'EXPORT';
export interface AuditTrailRecord {
  id: string;
  auditId: string;
  timestamp: string;
  actor: string;
  action: string;
  entityType: string;
  hashPreview: string;
  verificationStatus: 'VERIFIED' | 'TAMPER_EVIDENT';
}
