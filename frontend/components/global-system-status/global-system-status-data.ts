import { GlobalSystemStatusRecord } from './global-system-status-types';
export const MOCK_GLOBAL_SYSTEM_STATUSES: GlobalSystemStatusRecord[] = [
  { id: 'st1', statusId: 'STAT-AGP-001', subsystemName: 'Core Payment Gateway Engine', operatingRegion: 'us-east-1 (N. Virginia)', uptime90d: '99.999%', currentLatencyMs: 18, healthState: 'OPERATIONAL' },
  { id: 'st2', statusId: 'STAT-AGP-002', subsystemName: 'AgentGuard Policy Evaluator', operatingRegion: 'us-west-2 (Oregon)', uptime90d: '99.995%', currentLatencyMs: 14, healthState: 'OPERATIONAL' },
];
