import { AuditLogRecord } from './audit-log-types';
export const MOCK_AUDIT_LOGS: AuditLogRecord[] = [
  { id: 'a1', logId: 'AUD-LOG-001', actor: 'AGENT (AGT-892)', action: 'TRANSACTION_AUTHORIZED', resourceId: 'TXN-AGP-91F2', ipAddress: '10.240.0.12', timestamp: '2026-08-30 09:14:00', sha256Hash: 'sha256:7f8a9b2c...', integrity: 'VERIFIED' },
  { id: 'a2', logId: 'AUD-LOG-002', actor: 'SYSTEM (AgentGuard)', action: 'POLICY_EVALUATE_PASS', resourceId: 'AGP-GOV-001', ipAddress: '10.240.0.1', timestamp: '2026-08-30 09:13:59', sha256Hash: 'sha256:1a2b3c4d...', integrity: 'VERIFIED' },
];
