'use client';
export type PayoutSplitRulesTabType = 'SPLIT_RULES' | 'MARKETPLACE_REVENUE' | 'AGENT_COMMISSIONS' | 'AUDIT';
export interface PayoutSplitRuleRecord {
  id: string;
  ruleId: string;
  ruleName: string;
  platformShare: string;
  vendorShare: string;
  agentCommission: string;
  status: 'ACTIVE' | 'PAUSED';
}
