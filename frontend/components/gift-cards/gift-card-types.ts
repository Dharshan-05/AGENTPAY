'use client';
export type GiftCardsTabType = 'CARDS' | 'BALANCES' | 'ISSUANCE' | 'TRANSACTIONS' | 'SECURITY_VAULT' | 'EXPIRATION' | 'AUDIT';
export interface GiftCardRecord {
  id: string;
  giftCardId: string;
  codeMasked: string;
  initialBalance: string;
  currentBalance: string;
  currency: string;
  recipient: string;
  status: 'ACTIVE' | 'EXHAUSTED' | 'DISABLED';
}
