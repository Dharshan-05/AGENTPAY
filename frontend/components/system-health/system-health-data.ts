import { HealthRecord } from './system-health-types';
export const MOCK_HEALTH: HealthRecord[] = [
  { id: 'h1', componentId: 'SYS-HLT-001', name: 'Stripe Gateway Connector', type: 'PSP_CONNECTOR', uptime99: '99.99%', latencyMs: 142, status: 'OPERATIONAL' },
  { id: 'h2', componentId: 'SYS-HLT-002', name: 'AgentGuard Policy Engine', type: 'AI_ENGINE', uptime99: '100.00%', latencyMs: 12, status: 'OPERATIONAL' },
  { id: 'h3', componentId: 'SYS-HLT-003', name: 'FraudGuard Risk Evaluator', type: 'AI_ENGINE', uptime99: '99.98%', latencyMs: 28, status: 'OPERATIONAL' },
];
