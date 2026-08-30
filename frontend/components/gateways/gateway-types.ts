'use client';
export type GatewaysTabType = 'CONNECTORS' | 'ROUTING_RULES' | 'HEALTH' | 'LATENCY' | 'FAILOVER' | 'CONFIG' | 'AUDIT';
export interface GatewayRecord {
  id: string;
  gatewayId: string;
  name: string;
  provider: string;
  region: string;
  successRate: string;
  avgLatencyMs: number;
  status: 'ONLINE' | 'DEGRADED' | 'MAINTENANCE';
}
