import { TokenizationVaultRecord } from './tokenization-vault-types';
export const MOCK_TOKENIZATION_VAULT: TokenizationVaultRecord[] = [
  { id: 'v1', tokenId: 'VLT-AGP-001', surrogateToken: 'tok_vcard_91a82f03', tokenType: 'VIRTUAL_CARD', keyEncryptionKey: 'KEK-AES-256-v4', tokenExpiry: '2028-12-31', status: 'VAULTED' },
  { id: 'v2', tokenId: 'VLT-AGP-002', surrogateToken: 'tok_ach_44b109c1', tokenType: 'BANK_ACCOUNT', keyEncryptionKey: 'KEK-AES-256-v4', tokenExpiry: '2029-06-30', status: 'VAULTED' },
];
