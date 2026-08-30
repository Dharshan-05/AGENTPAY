'use client';
export type SegmentsTabType = 'COHORTS' | 'HIGH_VALUE' | 'RISK_TIERS' | 'INACTIVE' | 'ATTRIBUTES' | 'ANALYTICS' | 'AUDIT';
export interface SegmentRecord {
  id: string;
  segmentId: string;
  name: string;
  customerCount: number;
  totalVolume: string;
  riskProfile: 'LOW' | 'MEDIUM' | 'HIGH';
  status: 'ACTIVE' | 'SYSTEM';
}
