import { WalletRecord } from './wallet-types';
export const MOCK_WALLETS: WalletRecord[] = [
  { id: 'w1', walletId: 'WLT-AGP-001', name: 'Primary USD Treasury Vault', type: 'TREASURY_FIAT', addressOrAccount: 'JPMorgan •••• 9921', balance: '$2,480,500.00', currency: 'USD', status: 'ACTIVE' },
  { id: 'w2', walletId: 'WLT-AGP-002', name: 'USDC Agent Liquidity Vault', type: 'CRYPTO_VAULT', addressOrAccount: '0x71F...992A', balance: '1,500,000.00 USDC', currency: 'USDC', status: 'ACTIVE' },
];
