export type ApiKeyEnvironment = 'PRODUCTION' | 'SANDBOX';

export type ApiKeyScope =
  | 'FULL_ACCESS'
  | 'READ_ONLY'
  | 'PAYMENTS_ONLY'
  | 'AGENTS_WRITE'
  | 'GOVERNANCE_EVAL';

export type ApiKeyStatus = 'ACTIVE' | 'REVOKED' | 'ROTATION_REQUIRED' | 'SANDBOX';

export interface DeveloperApiKey {
  id: string;
  name: string;
  keyPrefix: string;
  environment: ApiKeyEnvironment;
  scopes: string[];
  status: ApiKeyStatus;
  created: string;
  lastUsed: string;
  requestRate: string;
  agentId: string;
  policyId: string;
  riskBand: 'LOW' | 'MEDIUM' | 'HIGH';
  fraudGuardStatus: 'CLEAN' | 'LOW' | 'MEDIUM';
  ipRestriction: boolean;
  rotationPeriod: '30 DAYS' | '90 DAYS' | '180 DAYS';
}

export interface WebhookEndpoint {
  id: string;
  url: string;
  events: string[];
  status: 'ACTIVE' | 'PAUSED' | 'DISABLED';
  deliveryRate: string;
  latency: string;
  lastEvent: string;
  signingSecret: string;
  created: string;
}

export interface WebhookEventRecord {
  id: string;
  event: string;
  endpointUrl: string;
  status: 'DELIVERED' | 'FAILED' | 'RETRYING';
  statusCode: number;
  latency: string;
  attempts: number;
  timestamp: string;
  signature: string;
  payload: Record<string, any>;
}

export interface SdkTestRequest {
  agentName: string;
  agentId: string;
  action: string;
  amount: string;
  currency: string;
  merchant: string;
  category: string;
  location: string;
  riskScore: number;
  policyId: string;
}

export interface SdkTestResponse {
  requestId: string;
  agentId: string;
  decision: 'AUTHORIZED' | 'REVIEW' | 'BLOCKED';
  riskScore: number;
  policy: string;
  fraudGuard: string;
  execution: string;
  latency: string;
  txnHash: string;
  timestamp: string;
}

export interface DeveloperRequestLog {
  id: string;
  requestId: string;
  method: 'GET' | 'POST' | 'DELETE' | 'PUT';
  endpoint: string;
  statusCode: number;
  latency: string;
  agentId: string;
  riskScore: number;
  agentGuardStatus: string;
  fraudGuardStatus: string;
  policyId: string;
  txnHash: string;
  timestamp: string;
}

export interface DeveloperSecurityPosture {
  activeKeysCount: number;
  rotationCompliance: string;
  ipRestrictionsEnforced: string;
  zeroTrustStatus: string;
  webhookSignaturesVerified: string;
}
