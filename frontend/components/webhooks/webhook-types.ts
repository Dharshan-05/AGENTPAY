// ============================================================
// AGENTPAY — PHASE 13B
// WEBHOOK & EVENT OPERATIONS — PRODUCTION TYPES
// ============================================================

export type WebhookTabType =
  | 'REGISTRY'
  | 'EVENTS'
  | 'DELIVERIES'
  | 'SUBSCRIPTIONS'
  | 'RETRIES'
  | 'SECURITY'
  | 'AUDIT';

export type EndpointStatus = 'HEALTHY' | 'DEGRADED' | 'FAILING' | 'ACTIVE' | 'PAUSED';

export type AuthType = 'HMAC_SHA256' | 'MTLS' | 'BEARER_TOKEN' | 'BASIC_AUTH';

export type EnvironmentType = 'PRODUCTION' | 'STAGING' | 'SANDBOX';

export type DeliveryStatus = 'DELIVERED' | 'FAILED' | 'RETRYING' | 'EXHAUSTED';

export interface WebhookEndpoint {
  id: string;
  endpointId: string;
  name: string;
  url: string;
  environment: EnvironmentType;
  subscribedEventsCount: number;
  status: EndpointStatus;
  healthScore: number;
  lastDelivery: string;
  successRate: number;
  p95LatencyMs: number;
  failedCount24h: number;
  secretMasked: string;
  secretRotationDays: number;
  authType: AuthType;
  createdAt: string;
  updatedAt: string;
}

export interface WebhookEventRecord {
  id: string;
  eventId: string;
  eventType: string;
  resourceType: string;
  resourceId: string;
  agentId: string;
  agentName: string;
  transactionId?: string;
  policyId?: string;
  severity: 'INFO' | 'WARNING' | 'HIGH' | 'CRITICAL';
  environment: EnvironmentType;
  deliveryCount: number;
  createdTimestamp: string;
  payloadJson: string;
}

export interface DeliveryAttempt {
  attemptNumber: number;
  timestamp: string;
  responseStatus: number;
  latencyMs: number;
  responseHeaders?: string;
  responseBodySnippet?: string;
  errorMessage?: string;
}

export interface WebhookDeliveryRecord {
  id: string;
  deliveryId: string;
  eventId: string;
  eventType: string;
  endpointId: string;
  endpointName: string;
  targetUrl: string;
  environment: EnvironmentType;
  createdTimestamp: string;
  completedTimestamp?: string;
  status: DeliveryStatus;
  responseStatus: number;
  latencyMs: number;
  attemptCount: number;
  maxRetries: number;
  signature: string;
  requestHeaders: string;
  payloadJson: string;
  responseBodySnippet: string;
  attempts: DeliveryAttempt[];
  agentId: string;
  transactionId?: string;
}

export interface WebhookSubscription {
  id: string;
  subscriptionId: string;
  endpointId: string;
  endpointName: string;
  eventPattern: string;
  environment: EnvironmentType;
  filterRule: string;
  status: 'ACTIVE' | 'PAUSED';
  createdTimestamp: string;
  lastTriggered: string;
}

export interface WebhookRetrySchedule {
  id: string;
  retryId: string;
  deliveryId: string;
  eventId: string;
  eventType: string;
  endpointName: string;
  targetUrl: string;
  attemptCount: number;
  maxAttempts: number;
  scheduledAt: string;
  lastError: string;
  status: 'QUEUED' | 'RETRYING' | 'EXHAUSTED';
}

export interface WebhookSecurityRecord {
  id: string;
  endpointId: string;
  endpointName: string;
  secretMasked: string;
  signatureAlgorithm: string;
  mTLSStatus: 'ENFORCED' | 'OPTIONAL' | 'DISABLED';
  timestampToleranceSeconds: number;
  ipAllowlist: string[];
  secretRotatedAt: string;
  secretRotationDueDays: number;
}

export interface WebhookAuditEvent {
  id: string;
  eventId: string;
  timestamp: string;
  actor: string;
  actorType: 'DEVELOPER' | 'SYSTEM' | 'AUTOMATION' | 'GOVERNANCE' | 'SECURITY_SERVICE';
  action: string;
  targetRef: string;
  details: string;
  ipAddress: string;
  auditHash: string;
}

export interface WebhookFilterState {
  searchQuery: string;
  status: string;
  eventType: string;
  endpoint: string;
  environment: string;
  httpStatus: string;
}
