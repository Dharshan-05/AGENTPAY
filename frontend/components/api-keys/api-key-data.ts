import { ApiKeyRecord } from './api-key-types';
export const MOCK_API_KEYS: ApiKeyRecord[] = [
  { id: 'ak1', keyId: 'AKEY-AGP-001', name: 'Production Agentic Autonomous Gateway Key', prefix: 'agp_live_8f3a...', scopes: 'payments:read, payments:write, agents:invoke', lastUsed: '2026-08-30 18:50:00', ipRestriction: '192.168.1.0/24 (Strict)', status: 'ACTIVE' },
  { id: 'ak2', keyId: 'AKEY-AGP-002', name: 'Staging Integration Telemetry Key', prefix: 'agp_test_4b12...', scopes: 'telemetry:read, audit:read', lastUsed: '2026-08-30 18:45:00', ipRestriction: 'ANY', status: 'ACTIVE' },
];
