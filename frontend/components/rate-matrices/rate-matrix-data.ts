import { RateMatrixRecord } from './rate-matrix-types';
export const MOCK_RATE_MATRICES: RateMatrixRecord[] = [
  { id: 'rm1', matrixId: 'RMAT-AGP-001', carrier: 'FedEx Express', serviceLevel: 'OVERNIGHT_PRIORITY', zone: 'ZONE_4_US', weightTier: '0 - 5 LBS', rateUSD: '$24.50', priority: 1, status: 'ACTIVE' },
  { id: 'rm2', matrixId: 'RMAT-AGP-002', carrier: 'DHL Express', serviceLevel: 'EXPRESS_WORLDWIDE', zone: 'ZONE_EU_INTL', weightTier: '0 - 10 LBS', rateUSD: '$48.00', priority: 1, status: 'ACTIVE' },
];
