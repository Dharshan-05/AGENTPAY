import { ThreeDSAuthenticationRecord } from './3ds-authentication-types';
export const MOCK_3DS_AUTHENTICATIONS: ThreeDSAuthenticationRecord[] = [
  { id: 't1', threeDSId: '3DS-AGP-001', paymentIntentRef: 'PI-AGP-91F2', authFlow: 'FRICTIONLESS', cavvResult: 'AAABBIIF00000000000', dsTransactionId: 'ds_tx_88a21f009', status: 'AUTHENTICATED' },
  { id: 't2', threeDSId: '3DS-AGP-002', paymentIntentRef: 'PI-AGP-4410', authFlow: 'CHALLENGE_SUCCESSFUL', cavvResult: 'AAABBAAF00000000000', dsTransactionId: 'ds_tx_441b92c10', status: 'AUTHENTICATED' },
];
