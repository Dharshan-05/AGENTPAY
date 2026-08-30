'use client';
export type TokenizationVaultTabType = 'VAULT_TOKENS' | 'KEY_ROTATION' | 'ENCRYPTION_POLICIES' | 'PCI_COMPLIANCE' | 'AUDIT';
export interface TokenizationVaultRecord {
  id: string;
  tokenId: string;
  surrogateToken: string;
  tokenType: 'VIRTUAL_CARD' | 'BANK_ACCOUNT' | 'PAYMENT_METHOD';
  keyEncryptionKey: string;
  tokenExpiry: string;
  status: 'VAULTED' | 'EXPIRED';
}
