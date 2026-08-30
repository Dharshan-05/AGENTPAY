'use client';
export type InvoicesTabType = 'REGISTRY' | 'ISSUED' | 'PAID' | 'OVERDUE' | 'CREDIT_NOTES' | 'LINE_ITEMS' | 'TAXES' | 'AUDIT';
export interface InvoiceRecord {
  id: string;
  invoiceId: string;
  customer: string;
  agentId: string;
  amount: string;
  taxAmount: string;
  dueDate: string;
  status: 'PAID' | 'OPEN' | 'UNCOLLECTIBLE' | 'VOID';
  paymentRef: string;
}
