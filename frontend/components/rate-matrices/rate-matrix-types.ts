'use client';
export type RateMatricesTabType = 'RATES' | 'PRIORITY_RULES' | 'FUEL_SURCHARGES' | 'ZONE_MAPS' | 'COMPARISON' | 'AUDIT';
export interface RateMatrixRecord {
  id: string;
  matrixId: string;
  carrier: string;
  serviceLevel: string;
  zone: string;
  weightTier: string;
  rateUSD: string;
  priority: number;
  status: 'ACTIVE' | 'ARCHIVED';
}
