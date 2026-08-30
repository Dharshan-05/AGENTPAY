import { GiftCardRecord } from './gift-card-types';
export const MOCK_GIFT_CARDS: GiftCardRecord[] = [
  { id: 'g1', giftCardId: 'GFT-AGP-001', codeMasked: '••••-••••-9921', initialBalance: '$1,000.00', currentBalance: '$650.00', currency: 'USD', recipient: 'Acme AI Labs', status: 'ACTIVE' },
  { id: 'g2', giftCardId: 'GFT-AGP-002', codeMasked: '••••-••••-4410', initialBalance: '€500.00', currentBalance: '€500.00', currency: 'EUR', recipient: 'Global Agentic Tech', status: 'ACTIVE' },
];
