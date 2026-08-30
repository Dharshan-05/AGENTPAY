'use client';
export type SubMerchantsTabType = 'MERCHANTS' | 'KYC_KYB_VERIFICATION' | 'SPLIT_ACCOUNTS' | 'PROCESSING_LIMITS' | 'AUDIT';
export interface SubMerchantRecord {
  id: string;
  subMerchantId: string;
  businessName: string;
  jurisdiction: string;
  kycKybStatus: 'VERIFIED' | 'PENDING_DOCUMENTATION' | 'UNDER_REVIEW';
  monthlyVolumeLimit: string;
  connectedAccountType: 'CUSTOM_EXPRESS' | 'STANDARD';
  status: 'ACTIVE' | 'RESTRICTED';
}
