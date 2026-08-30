import { VaultTokenMigrationRecord } from './vault-token-migration-types';
export const MOCK_VAULT_TOKEN_MIGRATIONS: VaultTokenMigrationRecord[] = [
  { id: 'v1', migrationId: 'VMIG-AGP-001', sourceVault: 'Stripe Vault US-East', targetVault: 'AGENTPAY_SECURE_VAULT', totalTokensMigrated: 45200, encryptionAlgorithm: 'AES-256-GCM', status: 'COMPLETED' },
  { id: 'v2', migrationId: 'VMIG-AGP-002', sourceVault: 'Adyen Vault EU-West', targetVault: 'AGENTPAY_SECURE_VAULT', totalTokensMigrated: 28400, encryptionAlgorithm: 'AES-256-GCM', status: 'COMPLETED' },
];
