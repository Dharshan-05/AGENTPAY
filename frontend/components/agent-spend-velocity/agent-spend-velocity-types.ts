'use client';
export type AgentSpendVelocityTabType = 'VELOCITY_LIMITS' | 'BURST_DETECTION' | 'HOURLY_WINDOW_MONITOR' | 'AUDIT';
export interface AgentSpendVelocityRecord {
  id: string;
  velocityId: string;
  agentRef: string;
  hourlyLimit: string;
  hourlySpent: string;
  burstThreshold: string;
  status: 'OPTIMAL' | 'NEAR_LIMIT';
}
