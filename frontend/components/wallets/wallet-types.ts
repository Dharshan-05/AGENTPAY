'use client';
export type WalletsTabType = 'REGISTRY' | 'TREASURY' | 'CRYPTO_VAULTS' | 'TRANSACTIONS' | 'KEYS' | 'HSM_SECURITY' | 'AUDIT';
export interface WalletRecord {
  id: string;
  walletId: string;
  name: string;
  type: 'TREASURY_FIAT' | 'CRYPTO_VAULT' | 'AGENT_EPHEMERAL';
  addressOrAccount: string;
  balance: string;
  currency: string;
  status: 'ACTIVE' | 'LOCKED';
}
