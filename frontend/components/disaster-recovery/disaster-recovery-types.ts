'use client';
export type DisasterRecoveryTabType = 'FAILOVER_NODES' | 'RPO_RTO_TELEMETRY' | 'BACKUP_SNAPSHOTS' | 'HA_HEALTH' | 'AUDIT';
export interface DisasterRecoveryRecord {
  id: string;
  disasterRecoveryId: string;
  region: string;
  failoverMode: 'AUTOMATED_HOT_STANDBY' | 'MULTI_REGION_ACTIVE_ACTIVE';
  rpoSeconds: number;
  rtoSeconds: number;
  lastDrTest: string;
  status: 'HEALTHY_ACTIVE' | 'STANDBY_READY';
}
