import { KycVerificationRecord } from './kyc-verification-types';
export const MOCK_KYC_VERIFICATIONS: KycVerificationRecord[] = [
  { id: 'k1', kycId: 'KYC-AGP-001', customerRef: 'CUS-AGP-001 (Jane Doe)', verificationLevel: 'TIER_3_ENTERPRISE', ocrScore: '99.8%', pepScreening: 'CLEAR', status: 'VERIFIED' },
  { id: 'k2', kycId: 'KYC-AGP-002', customerRef: 'CUS-AGP-002 (Acme Corp)', verificationLevel: 'TIER_3_ENTERPRISE', ocrScore: '99.5%', pepScreening: 'CLEAR', status: 'VERIFIED' },
];
