import { MerchantRecord } from './merchant-types';

export const MOCK_MERCHANTS: MerchantRecord[] = [
  { id: 'm1', merchantId: 'MER-AGP-001', businessName: 'Acme Cloud Services', country: 'US', industry: 'SaaS / Cloud', processor: 'Stripe', settlementCurrency: 'USD', volume: '$1,240,000.00', riskTier: 'LOW', accountStatus: 'ACTIVE', lastSettlement: 'Today 04:00' },
  { id: 'm2', merchantId: 'MER-AGP-002', businessName: 'Global AI Computing', country: 'DE', industry: 'AI Infrastructure', processor: 'Adyen', settlementCurrency: 'EUR', volume: '€890,000.00', riskTier: 'LOW', accountStatus: 'ACTIVE', lastSettlement: 'Yesterday' },
  { id: 'm3', merchantId: 'MER-AGP-003', businessName: 'Indic Commerce Vault', country: 'IN', industry: 'E-Commerce', processor: 'Razorpay', settlementCurrency: 'INR', volume: '₹12,500,000.00', riskTier: 'MEDIUM', accountStatus: 'VERIFIED', lastSettlement: 'Today 02:00' },
  { id: 'm4', merchantId: 'MER-AGP-004', businessName: 'Quantum Server Networks', country: 'US', industry: 'Hosting', processor: 'JPMorgan Direct', settlementCurrency: 'USD', volume: '$450,000.00', riskTier: 'HIGH', accountStatus: 'SUSPENDED', lastSettlement: '3d ago' },
];
