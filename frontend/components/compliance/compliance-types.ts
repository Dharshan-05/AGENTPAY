'use client';
export type ComplianceTabType = 'AML_SANCTIONS' | 'KYC_KYB' | 'PEP_CHECKS' | 'PEP_RESULTS' | 'RISK_TIERS' | 'REPORTS' | 'AUDIT';
export interface ComplianceRecord {
  id: string;
  complianceId: string;
  entityName: string;
  entityType: 'CUSTOMER' | 'MERCHANT' | 'AGENT_OWNER';
  checkType: 'AML_SANCTIONS' | 'KYC_VERIFICATION' | 'PEP_LIST';
  riskScore: number;
  status: 'CLEAR' | 'UNDER_REVIEW' | 'REJECTED';
}
