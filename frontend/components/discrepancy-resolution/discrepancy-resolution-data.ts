import { DiscrepancyResolutionRecord } from './discrepancy-resolution-types';
export const MOCK_DISCREPANCY_RESOLUTIONS: DiscrepancyResolutionRecord[] = [
  { id: 'd1', discrepancyId: 'DISC-AGP-001', ledgerEntryRef: 'LED-AGP-91F2', processorRef: 'TXN-STRIPE-881', varianceAmount: '$0.00', discrepancyReason: 'FEE_ROUNDING_ADJUSTMENT', resolutionStrategy: 'AUTOMATED_ZERO_VARIANCE_MATCH', status: 'RESOLVED' },
  { id: 'd2', discrepancyId: 'DISC-AGP-002', ledgerEntryRef: 'LED-AGP-4410', processorRef: 'TXN-ADYEN-412', varianceAmount: '$0.00', discrepancyReason: 'FX_MICRO_TIMING_VARIANCE', resolutionStrategy: 'AUTOMATED_FX_SPREAD_RECON', status: 'RESOLVED' },
];
