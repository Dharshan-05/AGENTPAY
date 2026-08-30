import { PayoutSplitRuleRecord } from './payout-split-rule-types';
export const MOCK_PAYOUT_SPLIT_RULES: PayoutSplitRuleRecord[] = [
  { id: 'sp1', ruleId: 'SPLT-AGP-001', ruleName: 'Standard 80/15/5 Marketplace Split', platformShare: '15.0%', vendorShare: '80.0%', agentCommission: '5.0%', status: 'ACTIVE' },
  { id: 'sp2', ruleId: 'SPLT-AGP-002', ruleName: 'Enterprise SaaS Direct Split', platformShare: '10.0%', vendorShare: '88.0%', agentCommission: '2.0%', status: 'ACTIVE' },
];
