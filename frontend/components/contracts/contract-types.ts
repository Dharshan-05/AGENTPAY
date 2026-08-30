'use client';
export type ContractsTabType = 'REGISTRY' | 'ACTIVE' | 'EXECUTION_LOGS' | 'STATE_MACHINES' | 'POLICY_BOUND' | 'TERMINATED' | 'AUDIT';
export interface ContractRecord {
  id: string;
  contractId: string;
  name: string;
  agentId: string;
  merchantId: string;
  spendCap: string;
  executionState: 'ACTIVE' | 'EXECUTING' | 'TERMINATED' | 'PAUSED';
  policyRef: string;
}
