import { AgentSpendVelocityRecord } from './agent-spend-velocity-types';
export const MOCK_AGENT_SPEND_VELOCITIES: AgentSpendVelocityRecord[] = [
  { id: 'v1', velocityId: 'VELO-AGP-001', agentRef: 'AGT-892 (High-Freq Trader)', hourlyLimit: '$10,000.00', hourlySpent: '$2,450.00', burstThreshold: '$3,000.00 / min', status: 'OPTIMAL' },
  { id: 'v2', velocityId: 'VELO-AGP-002', agentRef: 'AGT-441 (Cloud Procurement)', hourlyLimit: '$5,000.00', hourlySpent: '$1,890.00', burstThreshold: '$1,500.00 / min', status: 'OPTIMAL' },
];
