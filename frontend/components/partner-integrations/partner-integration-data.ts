import { PartnerIntegrationRecord } from './partner-integration-types';
export const MOCK_PARTNER_INTEGRATIONS: PartnerIntegrationRecord[] = [
  { id: 'i1', integrationId: 'INTG-AGP-001', partnerName: 'Stripe Connect Global', connectorType: 'PAYMENT_PROCESSOR', environment: 'PRODUCTION', apiLatencyMs: 42, healthStatus: 'HEALTHY' },
  { id: 'i2', integrationId: 'INTG-AGP-002', partnerName: 'Adyen N.V. European Gateway', connectorType: 'PAYMENT_PROCESSOR', environment: 'PRODUCTION', apiLatencyMs: 38, healthStatus: 'HEALTHY' },
];
