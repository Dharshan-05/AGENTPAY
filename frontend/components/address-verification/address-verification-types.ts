'use client';
export type AddressVerificationTabType = 'VERIFICATIONS' | 'GEO_RISK' | 'TAX_NEXUS' | 'CASS_STANDARDS' | 'RISK_SIGNALS' | 'AUDIT';
export interface AddressVerificationRecord {
  id: string;
  addressId: string;
  customerRef: string;
  type: 'BILLING' | 'SHIPPING' | 'BUSINESS';
  cityState: string;
  postalCode: string;
  verificationStatus: 'VERIFIED' | 'AMENDED' | 'FAILED';
  geoRiskScore: number;
  status: 'ACTIVE' | 'ARCHIVED';
}
