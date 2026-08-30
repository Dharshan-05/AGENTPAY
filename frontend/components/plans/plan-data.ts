import { PlanRecord } from './plan-types';
export const MOCK_PLANS: PlanRecord[] = [
  { id: 'p1', planId: 'PLN-AGP-001', name: 'Enterprise Autonomy Tier', tier: 'ENTERPRISE', monthlyPrice: '$4,999.00', annualPrice: '$49,990.00', agentLimit: 100, status: 'ACTIVE' },
  { id: 'p2', planId: 'PLN-AGP-002', name: 'Growth Agent Plan', tier: 'PRO', monthlyPrice: '$999.00', annualPrice: '$9,990.00', agentLimit: 20, status: 'ACTIVE' },
];
