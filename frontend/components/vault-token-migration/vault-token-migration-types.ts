'use client';
export type VaultTokenMigrationTabType = 'MIGRATION_JOBS' | 'PORTABILITY_EXPORTS' | 'KEY_RE_ENCRYPTION' | 'AUDIT';
export interface VaultTokenMigrationRecord {
  id: string;
  migrationId: string;
  sourceVault: string;
  targetVault: string;
  totalTokensMigrated: number;
  encryptionAlgorithm: string;
  status: 'COMPLETED' | 'IN_PROGRESS';
}
