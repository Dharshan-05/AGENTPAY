import { ContractRecord } from './contract-types';
export const MOCK_CONTRACTS: ContractRecord[] = [
  { id: 'c1', contractId: 'CTR-AGP-001', name: 'Autonomous Vendor Procurement SLA', agentId: 'AGT-892', merchantId: 'MER-AGP-001', spendCap: '$100,000.00', executionState: 'ACTIVE', policyRef: 'AGP-GOV-001' },
  { id: 'c2', contractId: 'CTR-AGP-002', name: 'APAC Liquidity Rebalancing Contract', agentId: 'AGT-118', merchantId: 'MER-AGP-003', spendCap: '₹10,000,000.00', executionState: 'ACTIVE', policyRef: 'AGP-GOV-003' },
];
