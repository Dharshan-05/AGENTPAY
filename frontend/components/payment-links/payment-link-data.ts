import { PaymentLinkRecord } from './payment-link-types';
export const MOCK_PAYMENT_LINKS: PaymentLinkRecord[] = [
  { id: 'l1', linkId: 'LNK-AGP-001', url: 'https://pay.agentpay.ai/lnk_99182a', amount: '$1,250.00', customer: 'CUS-AGP-001', usageLimit: '1 / Single Use', status: 'ACTIVE', expiresAt: '2026-09-01' },
  { id: 'l2', linkId: 'LNK-AGP-002', url: 'https://pay.agentpay.ai/lnk_4410cc', amount: '€500.00', customer: 'CUS-AGP-002', usageLimit: 'Unlimited', status: 'ACTIVE', expiresAt: '2026-09-15' },
];
