import { ComplianceRecord } from './compliance-types';
export const MOCK_COMPLIANCE: ComplianceRecord[] = [
  { id: 'c1', complianceId: 'CMP-AGP-001', entityName: 'Acme AI Systems LLC', entityType: 'MERCHANT', checkType: 'AML_SANCTIONS', riskScore: 4, status: 'CLEAR' },
  { id: 'c2', complianceId: 'CMP-AGP-002', entityName: 'Global Autonomous Tech', entityType: 'CUSTOMER', checkType: 'KYC_VERIFICATION', riskScore: 8, status: 'CLEAR' },
];
