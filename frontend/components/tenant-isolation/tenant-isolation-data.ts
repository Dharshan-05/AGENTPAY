import { TenantIsolationRecord } from './tenant-isolation-types';
export const MOCK_TENANT_ISOLATIONS: TenantIsolationRecord[] = [
  { id: 'tn1', tenantId: 'TNT-AGP-001', organizationName: 'Acme Enterprise Holdings', isolationTier: 'VIRTUAL_PRIVATE_LEDGER', allocatedQuota: '100,000 Txns / min', complianceLevel: 'SOC2 TYPE II', status: 'ACTIVE' },
  { id: 'tn2', tenantId: 'TNT-AGP-002', organizationName: 'Global Fintech Ventures', isolationTier: 'VIRTUAL_PRIVATE_LEDGER', allocatedQuota: '50,000 Txns / min', complianceLevel: 'SOC2 TYPE II', status: 'ACTIVE' },
];
