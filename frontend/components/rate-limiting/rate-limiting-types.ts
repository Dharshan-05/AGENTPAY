'use client';
export type RateLimitingTabType = 'LIMIT_POLICIES' | 'BURST_CONTROLS' | 'THROTTLED_CLIENTS' | 'IP_BUCKETS' | 'AUDIT';
export interface RateLimitingRecord {
  id: string;
  limitId: string;
  clientRef: string;
  maxRps: number;
  burstCapacity: number;
  currentRps: number;
  throttledRequests24h: number;
  status: 'ENFORCED' | 'DEGRADED';
}
