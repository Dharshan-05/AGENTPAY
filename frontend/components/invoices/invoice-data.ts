import { InvoiceRecord } from './invoice-types';
export const MOCK_INVOICES: InvoiceRecord[] = [
  { id: 'i1', invoiceId: 'INV-AGP-001', customer: 'CUS-AGP-001', agentId: 'AGT-892', amount: '$4,820.00', taxAmount: '$385.60', dueDate: '2026-09-15', status: 'PAID', paymentRef: 'TXN-AGP-91F2' },
  { id: 'i2', invoiceId: 'INV-AGP-002', customer: 'CUS-AGP-002', agentId: 'AGT-441', amount: '$12,500.00', taxAmount: '$1,000.00', dueDate: '2026-09-10', status: 'OPEN', paymentRef: 'PENDING' },
];
