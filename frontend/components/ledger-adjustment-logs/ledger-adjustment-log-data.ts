import { LedgerAdjustmentRecord } from './ledger-adjustment-log-types';
export const MOCK_LEDGER_ADJUSTMENTS: LedgerAdjustmentRecord[] = [
  { id: 'la1', adjustmentId: 'LADJ-AGP-001', ledgerAccount: 'ACC-AGP-1001 (Reserve Account)', adjustmentType: 'CREDIT_OFFSET', amount: '$1,250.00', reasonCode: 'PROCESSOR_FEE_REBALANCING', approverRef: 'USR-FIN-001 (Senior Controller)', status: 'POSTED_IMMUTABLE' },
  { id: 'la2', adjustmentId: 'LADJ-AGP-002', ledgerAccount: 'ACC-AGP-2004 (Clearing House)', adjustmentType: 'DEBIT_CORRECTION', amount: '$420.00', reasonCode: 'FX_VARIANCE_ADJUSTMENT', approverRef: 'USR-FIN-002 (Treasury Manager)', status: 'POSTED_IMMUTABLE' },
];
