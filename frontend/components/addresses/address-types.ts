'use client';
export type AddressesTabType = 'REGISTRY' | 'GEO_VERIFICATION' | 'CUSTOMER_LINKAGE' | 'MERCHANT_LOCATIONS' | 'RISK_PROFILING' | 'AUDIT';
export interface AddressRecord {
  id: string;
  addressId: string;
  entityName: string;
  type: 'BILLING' | 'SHIPPING' | 'BUSINESS' | 'WAREHOUSE';
  street: string;
  cityStateZip: string;
  country: string;
  verificationStatus: 'VERIFIED' | 'UNVERIFIED' | 'RISK_FLAGGED';
}
