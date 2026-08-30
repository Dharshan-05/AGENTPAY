import { AddressVerificationRecord } from './address-verification-types';
export const MOCK_ADDRESS_VERIFICATION: AddressVerificationRecord[] = [
  { id: 'av1', addressId: 'AVER-AGP-001', customerRef: 'CUS-AGP-001', type: 'BILLING', cityState: 'San Francisco, CA', postalCode: '94105', verificationStatus: 'VERIFIED', geoRiskScore: 4, status: 'ACTIVE' },
  { id: 'av2', addressId: 'AVER-AGP-002', customerRef: 'CUS-AGP-002', type: 'SHIPPING', cityState: 'Frankfurt, DE', postalCode: '60311', verificationStatus: 'VERIFIED', geoRiskScore: 8, status: 'ACTIVE' },
];
