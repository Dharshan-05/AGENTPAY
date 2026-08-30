import { LedgerEntryRecord } from './ledger-types';

export const MOCK_LEDGER: LedgerEntryRecord[] = [
  { id: 'l1', entryId: 'LED-AGP-001', journalId: 'JRN-2026-0830-01', accountName: '1000 — Settlement Clearing', debit: '$781,680.00', credit: '$0.00', currency: 'USD', transactionRef: 'TXN-AGP-91F2', timestamp: '2026-08-30 09:14:00', prevHash: 'sha256:0000...0000', currentHash: 'sha256:7f8a9b2c3d4e...', integrityState: 'VERIFIED' },
  { id: 'l2', entryId: 'LED-AGP-002', journalId: 'JRN-2026-0830-01', accountName: '4000 — Merchant Payout Payable', debit: '$0.00', credit: '$776,831.00', currency: 'USD', transactionRef: 'TXN-AGP-91F2', timestamp: '2026-08-30 09:14:00', prevHash: 'sha256:7f8a9b2c3d4e...', currentHash: 'sha256:1a2b3c4d5e6f...', integrityState: 'VERIFIED' },
  { id: 'l3', entryId: 'LED-AGP-003', journalId: 'JRN-2026-0830-01', accountName: '5000 — Interchange Fee Expense', debit: '$4,849.00', credit: '$0.00', currency: 'USD', transactionRef: 'TXN-AGP-91F2', timestamp: '2026-08-30 09:14:00', prevHash: 'sha256:1a2b3c4d5e6f...', currentHash: 'sha256:9900aabbccdd...', integrityState: 'VERIFIED' },
];
