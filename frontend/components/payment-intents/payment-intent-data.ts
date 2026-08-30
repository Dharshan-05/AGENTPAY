import { PaymentIntentRecord } from './payment-intent-types';

export const MOCK_INTENTS: PaymentIntentRecord[] = [
  { id: 'pi1', intentId: 'PI-AGP-001', amount: '$4,820.00', currency: 'USD', customer: 'CUS-AGP-001', agentId: 'AGT-892', paymentMethod: 'VISA •••• 4821', status: 'SUCCEEDED', processor: 'Stripe', riskScore: 12, authCode: 'AUTH-99120', createdAt: '2m ago' },
  { id: 'pi2', intentId: 'PI-AGP-002', amount: '$12,500.00', currency: 'USD', customer: 'CUS-AGP-002', agentId: 'AGT-441', paymentMethod: 'BANK •••• 9921', status: 'AUTHORIZED', processor: 'JPMorgan Direct', riskScore: 8, authCode: 'AUTH-44100', createdAt: '18m ago' },
  { id: 'pi3', intentId: 'PI-AGP-003', amount: '₹150,000.00', currency: 'INR', customer: 'CUS-AGP-003', agentId: 'AGT-118', paymentMethod: 'agentpay•••@hdfc', status: 'PROCESSING', processor: 'Razorpay', riskScore: 35, authCode: 'AUTH-11800', createdAt: '45m ago' },
  { id: 'pi4', intentId: 'PI-AGP-004', amount: '€1,500.00', currency: 'EUR', customer: 'CUS-AGP-004', agentId: 'AGT-990', paymentMethod: 'MC •••• 9901', status: 'FAILED', processor: 'Adyen', riskScore: 78, authCode: 'DECLINED_3DS', createdAt: '2h ago' },
];
