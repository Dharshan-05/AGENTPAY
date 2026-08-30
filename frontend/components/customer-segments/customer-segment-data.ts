import { SegmentRecord } from './customer-segment-types';
export const MOCK_SEGMENTS: SegmentRecord[] = [
  { id: 'sg1', segmentId: 'SEG-AGP-001', name: 'Enterprise High-Volume Cohort', customerCount: 14, totalVolume: '$4.82M', riskProfile: 'LOW', status: 'ACTIVE' },
  { id: 'sg2', segmentId: 'SEG-AGP-002', name: 'High-Risk Velocity Cohort', customerCount: 3, totalVolume: '$120.0K', riskProfile: 'HIGH', status: 'ACTIVE' },
];
