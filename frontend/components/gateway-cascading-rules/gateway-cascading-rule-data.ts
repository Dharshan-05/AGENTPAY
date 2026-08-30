import { GatewayCascadingRuleRecord } from './gateway-cascading-rule-types';
export const MOCK_GATEWAY_CASCADING_RULES: GatewayCascadingRuleRecord[] = [
  { id: 'c1', cascadingId: 'CASC-AGP-001', ruleName: 'US Card High-Velocity Cascade', primaryPsp: 'STRIPE_CONNECT', fallbackPsp: 'ADYEN_GLOBAL', maxRetries: 2, failoverLatencySlaMs: 45, status: 'ACTIVE' },
  { id: 'c2', cascadingId: 'CASC-AGP-002', ruleName: 'EU SEPA Instant Smart Cascade', primaryPsp: 'ADYEN_GLOBAL', fallbackPsp: 'JPMORGAN_CHASE', maxRetries: 2, failoverLatencySlaMs: 38, status: 'ACTIVE' },
];
