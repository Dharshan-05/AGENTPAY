'use client';
export type PartnerIntegrationsTabType = 'CONNECTORS' | 'CREDENTIAL_VAULT' | 'SANDBOX_TESTING' | 'HEALTH_TELEMETRY' | 'AUDIT';
export interface PartnerIntegrationRecord {
  id: string;
  integrationId: string;
  partnerName: string;
  connectorType: 'PAYMENT_PROCESSOR' | 'BANK_GATEWAY' | 'FRAUD_ENGINE';
  environment: 'PRODUCTION' | 'SANDBOX';
  apiLatencyMs: number;
  healthStatus: 'HEALTHY' | 'DEGRADED';
}
