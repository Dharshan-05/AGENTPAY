import { GatewayRoutingRecord } from './gateway-routing-types';
export const MOCK_GATEWAY_ROUTING: GatewayRoutingRecord[] = [
  { id: 'gr1', ruleId: 'GROUT-AGP-001', ruleName: 'US Card High-Value Least-Cost Route', primaryGateway: 'STRIPE_CONNECT', fallbackGateway: 'ADYEN_GLOBAL', condition: 'USD && Amount >= $1,000.00', successRate: '99.94%', status: 'ACTIVE' },
  { id: 'gr2', ruleId: 'GROUT-AGP-002', ruleName: 'EU SEPA Instant Smart Cascade', primaryGateway: 'ADYEN_GLOBAL', fallbackGateway: 'JPMORGAN_CHASE', condition: 'EUR && Method == SEPA_INSTANT', successRate: '99.88%', status: 'ACTIVE' },
];
