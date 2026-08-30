'use client';
export type SystemTelemetryTabType = 'NODES' | 'LATENCY_MAP' | 'UPTIME' | 'SECURITY_HEARTBEAT' | 'AUDIT';
export interface SystemTelemetryRecord {
  id: string;
  nodeId: string;
  region: string;
  serviceName: string;
  latencyMs: number;
  uptimePercent: string;
  status: 'HEALTHY' | 'DEGRADED';
}
