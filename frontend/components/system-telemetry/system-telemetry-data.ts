import { SystemTelemetryRecord } from './system-telemetry-types';
export const MOCK_SYSTEM_TELEMETRY: SystemTelemetryRecord[] = [
  { id: 'st1', nodeId: 'STEL-AGP-001', region: 'us-east-1 (N. Virginia)', serviceName: 'AGENTGUARD_POLICY_ENGINE', latencyMs: 14, uptimePercent: '99.999%', status: 'HEALTHY' },
  { id: 'st2', nodeId: 'STEL-AGP-002', region: 'eu-central-1 (Frankfurt)', serviceName: 'FRAUDGUARD_NEURAL_ROUTER', latencyMs: 18, uptimePercent: '99.995%', status: 'HEALTHY' },
];
