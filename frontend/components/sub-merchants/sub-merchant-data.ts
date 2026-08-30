import { SubMerchantRecord } from './sub-merchant-types';
export const MOCK_SUB_MERCHANTS: SubMerchantRecord[] = [
  { id: 'sm1', subMerchantId: 'SUBM-AGP-001', businessName: 'Acme Agentic Solutions LLC', jurisdiction: 'United States (Delaware)', kycKybStatus: 'VERIFIED', monthlyVolumeLimit: '$500,000.00', connectedAccountType: 'CUSTOM_EXPRESS', status: 'ACTIVE' },
  { id: 'sm2', subMerchantId: 'SUBM-AGP-002', businessName: 'Global AI Marketplace GmbH', jurisdiction: 'Germany (Frankfurt)', kycKybStatus: 'VERIFIED', monthlyVolumeLimit: '€750,000.00', connectedAccountType: 'CUSTOM_EXPRESS', status: 'ACTIVE' },
];
