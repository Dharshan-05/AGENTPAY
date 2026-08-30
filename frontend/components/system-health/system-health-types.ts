'use client';
export type HealthTabType = 'OVERVIEW' | 'LATENCY_MAP' | 'CIRCUIT_BREAKERS' | 'Uptime' | 'CONNECTORS' | 'INCIDENTS' | 'AUDIT';
export interface HealthRecord {
  id: string;
  componentId: string;
  name: string;
  type: 'PSP_CONNECTOR' | 'DATABASE' | 'EVENT_BUS' | 'AI_ENGINE';
  uptime99: string;
  latencyMs: number;
  status: 'OPERATIONAL' | 'DEGRADED' | 'MAINTENANCE';
}
