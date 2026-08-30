import { AuditTrailRecord } from './audit-trail-types';
export const MOCK_AUDIT_TRAILS: AuditTrailRecord[] = [
  { id: 'au1', auditId: 'AUDT-AGP-001', timestamp: '2026-08-30 18:14:02', actor: 'AGENT-892', action: 'PAYMENT_INTENT_EVALUATED', entityType: 'PAYMENT_INTENT', hashPreview: 'sha256:a3f2e1...9b12', verificationStatus: 'VERIFIED' },
  { id: 'au2', auditId: 'AUDT-AGP-002', timestamp: '2026-08-30 18:15:20', actor: 'SYSTEM_ROUTER', action: 'GATEWAY_CASCADE_SWITCH', entityType: 'GATEWAY_ROUTER', hashPreview: 'sha256:7c9e04...4a18', verificationStatus: 'VERIFIED' },
];
