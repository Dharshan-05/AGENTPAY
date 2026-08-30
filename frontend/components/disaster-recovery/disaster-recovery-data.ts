import { DisasterRecoveryRecord } from './disaster-recovery-types';
export const MOCK_DISASTER_RECOVERIES: DisasterRecoveryRecord[] = [
  { id: 'dr1', disasterRecoveryId: 'DR-AGP-001', region: 'us-west-2 (Oregon)', failoverMode: 'AUTOMATED_HOT_STANDBY', rpoSeconds: 0, rtoSeconds: 2, lastDrTest: '2026-08-28', status: 'HEALTHY_ACTIVE' },
  { id: 'dr2', disasterRecoveryId: 'DR-AGP-002', region: 'eu-west-1 (Ireland)', failoverMode: 'MULTI_REGION_ACTIVE_ACTIVE', rpoSeconds: 0, rtoSeconds: 1, lastDrTest: '2026-08-28', status: 'HEALTHY_ACTIVE' },
];
