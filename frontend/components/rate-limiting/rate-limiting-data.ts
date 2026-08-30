import { RateLimitingRecord } from './rate-limiting-types';
export const MOCK_RATE_LIMITINGS: RateLimitingRecord[] = [
  { id: 'r1', limitId: 'RLIM-AGP-001', clientRef: 'AGT-892 (Trading Bot)', maxRps: 500, burstCapacity: 1000, currentRps: 142, throttledRequests24h: 0, status: 'ENFORCED' },
  { id: 'r2', limitId: 'RLIM-AGP-002', clientRef: 'AGT-441 (Procurement)', maxRps: 200, burstCapacity: 400, currentRps: 88, throttledRequests24h: 0, status: 'ENFORCED' },
];
