'use client';
export type GatewayCascadingRulesTabType = 'CASCADING_RULES' | 'FAILOVER_STRATEGIES' | 'PSP_LATENCY_MATRIX' | 'AUDIT';
export interface GatewayCascadingRuleRecord {
  id: string;
  cascadingId: string;
  ruleName: string;
  primaryPsp: string;
  fallbackPsp: string;
  maxRetries: number;
  failoverLatencySlaMs: number;
  status: 'ACTIVE' | 'PAUSED';
}
