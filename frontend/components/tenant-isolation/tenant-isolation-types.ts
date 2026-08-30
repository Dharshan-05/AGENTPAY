'use client';
export type TenantIsolationTabType = 'TENANTS' | 'ROW_LEVEL_ISOLATION' | 'VIRTUAL_PLATFORMS' | 'RBAC_POLICIES' | 'AUDIT';
export interface TenantIsolationRecord {
  id: string;
  tenantId: string;
  organizationName: string;
  isolationTier: 'VIRTUAL_PRIVATE_LEDGER' | 'ROW_LEVEL_STRICT';
  allocatedQuota: string;
  complianceLevel: string;
  status: 'ACTIVE' | 'ISOLATED';
}
