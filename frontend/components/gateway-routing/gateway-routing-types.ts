'use client';
export type GatewayRoutingTabType = 'ROUTING_RULES' | 'CASCADING' | 'PSP_HEALTH' | 'COST_OPTIMIZER' | 'AUDIT';
export interface GatewayRoutingRecord {
  id: string;
  ruleId: string;
  ruleName: string;
  primaryGateway: string;
  fallbackGateway: string;
  condition: string;
  successRate: string;
  status: 'ACTIVE' | 'PAUSED';
}
