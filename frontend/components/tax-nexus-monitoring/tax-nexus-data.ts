import { TaxNexusRecord } from './tax-nexus-types';
export const MOCK_TAX_NEXUSES: TaxNexusRecord[] = [
  { id: 'n1', nexusId: 'NEX-AGP-001', jurisdiction: 'United States — California (CA)', salesVolume: '$542,000.00', thresholdLimit: '$500,000.00', percentageReached: '108.4%', nexusStatus: 'NEXUS_REACHED' },
  { id: 'n2', nexusId: 'NEX-AGP-002', jurisdiction: 'United States — New York (NY)', salesVolume: '$418,500.00', thresholdLimit: '$500,000.00', percentageReached: '83.7%', nexusStatus: 'APPROACHING_THRESHOLD' },
];
