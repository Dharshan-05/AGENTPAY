'use client';
export type GlobalSystemStatusTabType = 'SYSTEM_STATUS' | 'REGION_LATENCY_MAP' | 'INCIDENT_HISTORY' | 'SLA_METRICS' | 'AUDIT';
export interface GlobalSystemStatusRecord {
  id: string;
  statusId: string;
  subsystemName: string;
  operatingRegion: string;
  uptime90d: string;
  currentLatencyMs: number;
  healthState: 'OPERATIONAL' | 'DEGRADED_PERFORMANCE';
}
