'use client';
export type PaymentLinksTabType = 'REGISTRY' | 'ACTIVE_LINKS' | 'COMPLETED' | 'EXPIRED' | 'QR_CODES' | 'ANALYTICS' | 'AUDIT';
export interface PaymentLinkRecord {
  id: string;
  linkId: string;
  url: string;
  amount: string;
  customer: string;
  usageLimit: string;
  status: 'ACTIVE' | 'COMPLETED' | 'EXPIRED';
  expiresAt: string;
}
