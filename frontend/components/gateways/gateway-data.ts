import { GatewayRecord } from './gateway-types';
export const MOCK_GATEWAYS: GatewayRecord[] = [
  { id: 'g1', gatewayId: 'GW-AGP-001', name: 'Stripe Global Connector', provider: 'Stripe', region: 'us-east-1', successRate: '99.94%', avgLatencyMs: 142, status: 'ONLINE' },
  { id: 'g2', gatewayId: 'GW-AGP-002', name: 'Adyen EU Core', provider: 'Adyen', region: 'eu-west-1', successRate: '99.98%', avgLatencyMs: 118, status: 'ONLINE' },
  { id: 'g3', gatewayId: 'GW-AGP-003', name: 'Razorpay APAC Direct', provider: 'Razorpay', region: 'ap-south-1', successRate: '99.85%', avgLatencyMs: 189, status: 'ONLINE' },
];
