'use client';
export type ThreeDSAuthenticationTabType = 'AUTHENTICATIONS' | 'FRICTIONLESS' | 'CHALLENGES' | 'EXEMPTION_ENGINE' | 'AUDIT';
export interface ThreeDSAuthenticationRecord {
  id: string;
  threeDSId: string;
  paymentIntentRef: string;
  authFlow: 'FRICTIONLESS' | 'CHALLENGE_SUCCESSFUL' | 'EXEMPTED';
  cavvResult: string;
  dsTransactionId: string;
  status: 'AUTHENTICATED' | 'REJECTED';
}
