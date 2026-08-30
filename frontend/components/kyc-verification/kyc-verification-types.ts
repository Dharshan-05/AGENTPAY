'use client';
export type KycVerificationTabType = 'VERIFICATIONS' | 'DOCUMENT_OCR' | 'FACIAL_BIOMETRICS' | 'PEP_CHECKS' | 'AUDIT';
export interface KycVerificationRecord {
  id: string;
  kycId: string;
  customerRef: string;
  verificationLevel: 'TIER_1_BASIC' | 'TIER_2_ADVANCED' | 'TIER_3_ENTERPRISE';
  ocrScore: string;
  pepScreening: 'CLEAR' | 'FLAGGED';
  status: 'VERIFIED' | 'UNDER_REVIEW';
}
