import { SessionControlRecord } from './session-control-types';
export const MOCK_SESSION_CONTROL: SessionControlRecord[] = [
  { id: 'sc1', sessionId: 'SCTL-AGP-001', agentRef: 'AGT-892', ipAddressMasked: '192.168.1.•••', authMethod: 'MUTUAL_TLS', riskScore: 2, status: 'ACTIVE' },
  { id: 'sc2', sessionId: 'SCTL-AGP-002', agentRef: 'AGT-441', ipAddressMasked: '10.0.4.•••', authMethod: 'JWT_BEARER', riskScore: 12, status: 'ACTIVE' },
];
