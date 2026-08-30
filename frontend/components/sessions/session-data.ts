import { SessionRecord } from './session-types';
export const MOCK_SESSIONS: SessionRecord[] = [
  { id: 's1', sessionId: 'SES-AGP-001', customer: 'CUS-AGP-001', merchant: 'MER-AGP-001', agentId: 'AGT-892', amount: '$12,999.00', ttlExpiresAt: '2026-08-30 09:44:00', status: 'COMPLETED' },
  { id: 's2', sessionId: 'SES-AGP-002', customer: 'CUS-AGP-002', merchant: 'MER-AGP-002', agentId: 'AGT-441', amount: '€2,499.00', ttlExpiresAt: '2026-08-30 10:15:00', status: 'OPEN' },
];
