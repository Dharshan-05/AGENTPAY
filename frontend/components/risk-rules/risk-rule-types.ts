'use client';

export type RiskRulesTabType = 'REGISTRY' | 'RULES' | 'CONDITIONS' | 'ACTIONS' | 'TESTING' | 'DECISIONS' | 'PERFORMANCE' | 'AUDIT';

export interface RiskRuleRecord {
  id: string;
  ruleId: string;
  name: string;
  priority: number;
  condition: string;
  action: 'ALLOW' | 'REVIEW' | 'BLOCK' | 'HITL';
  riskThreshold: number;
  agentScope: string;
  merchantScope: string;
  status: 'ACTIVE' | 'TESTING' | 'DISABLED';
  triggeredCount: number;
  falsePositiveRate: string;
  lastExecution: string;
}
