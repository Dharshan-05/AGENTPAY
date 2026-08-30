'use client';

export type LedgerTabType = 'ENTRIES' | 'ACCOUNTS' | 'JOURNALS' | 'TRANSACTIONS' | 'SETTLEMENTS' | 'RECONCILIATION' | 'INTEGRITY' | 'AUDIT';

export interface LedgerEntryRecord {
  id: string;
  entryId: string;
  journalId: string;
  accountName: string;
  debit: string;
  credit: string;
  currency: string;
  transactionRef: string;
  timestamp: string;
  prevHash: string;
  currentHash: string;
  integrityState: 'VERIFIED' | 'CHAIN_VALID';
}
