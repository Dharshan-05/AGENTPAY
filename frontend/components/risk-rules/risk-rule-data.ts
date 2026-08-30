import { RiskRuleRecord } from './risk-rule-types';

export const MOCK_RISK_RULES: RiskRuleRecord[] = [
  { id: 'rr1', ruleId: 'RSK-RULE-001', name: 'Velocity Anomaly Guard', priority: 1, condition: 'txnCount > 10 in 60s OR velocityScore > 80', action: 'BLOCK', riskThreshold: 80, agentScope: 'ALL AGENTS', merchantScope: 'ALL MERCHANTS', status: 'ACTIVE', triggeredCount: 142, falsePositiveRate: '0.02%', lastExecution: '2m ago' },
  { id: 'rr2', ruleId: 'RSK-RULE-002', name: 'High-Value HITL Trigger', priority: 2, condition: 'txnAmount > $10,000.00 AND agentRating == UNTRUSTED', action: 'HITL', riskThreshold: 60, agentScope: 'AGT-441', merchantScope: 'ALL MERCHANTS', status: 'ACTIVE', triggeredCount: 28, falsePositiveRate: '0.10%', lastExecution: '18m ago' },
  { id: 'rr3', ruleId: 'RSK-RULE-003', name: 'Geo Mismatch Fraud Review', priority: 3, condition: 'cardCountry != agentIPCountry', action: 'REVIEW', riskThreshold: 50, agentScope: 'ALL AGENTS', merchantScope: 'ALL MERCHANTS', status: 'ACTIVE', triggeredCount: 89, falsePositiveRate: '0.45%', lastExecution: '45m ago' },
];
