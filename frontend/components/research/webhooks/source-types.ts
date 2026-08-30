// ============================================================
// AGENTPAY — PHASE 13A
// WEBHOOK & EVENT OPERATIONS — SOURCE TYPES
// Research baseline type definitions
// ============================================================

export type WebhookSourceTabType =
  | 'REGISTRY'
  | 'EVENTS'
  | 'DELIVERIES'
  | 'SUBSCRIPTIONS'
  | 'RETRIES'
  | 'SECURITY'
  | 'AUDIT';

export type WebhookEndpointStatus = 'ACTIVE' | 'PAUSED' | 'HEALTHY' | 'DEGRADED' | 'FAILING' | 'DISABLED';

export type DeliveryStatus = 'DELIVERED' | 'FAILED' | 'RETRYING' | 'EXHAUSTED' | 'BLOCKED' | 'SKIPPED';

export type EnvironmentType = 'PRODUCTION' | 'STAGING' | 'SANDBOX';

export type EventSeverity = 'INFO' | 'WARNING' | 'CRITICAL';

export interface WebhookEndpoint {
  id: string;
  endpointId: string;
  name: string;
  url: string;
  environment: EnvironmentType;
  subscribedEventsCount: number;
  status: WebhookEndpointStatus;
  healthScore: number;
  lastDelivery: string;
  successRate: number;
  p95LatencyMs: number;
  failedCount24h: number;
  secretMasked: string;
  secretRotationDays: number;
  authType: 'HMAC_SHA256' | 'MTLS' | 'BEARER_TOKEN' | 'BASIC_AUTH';
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
  severity: EventSeverity;
  environment: EnvironmentType;
  payloadJson: string;
  deliveryCount: number;
  createdTimestamp: string;
}

export interface WebhookSubscription {
  id: string;
  subscriptionId: string;
  endpointId: string;
  endpointName: string;
  eventPattern: string;
  environment: EnvironmentType;
  filterRule: string;
  status: 'ACTIVE' | 'PAUSED' | 'DISABLED';
  createdTimestamp: string;
  lastTriggered: string;
}

export interface WebhookAttempt {
  attemptNumber: number;
  timestamp: string;
  responseStatus: number;
  latencyMs: number;
  errorMessage?: string;
  responseHeaders?: string;
  responseBodySnippet?: string;
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
  nextRetryAt?: string;
  signature: string;
  requestHeaders: string;
  payloadJson: string;
  responseBodySnippet?: string;
  attempts: WebhookAttempt[];
  agentId: string;
  transactionId?: string;
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
  status: 'QUEUED' | 'EXHAUSTED' | 'REPLAYED' | 'CANCELLED';
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
  actorType: 'DEVELOPER' | 'SYSTEM' | 'AGENT' | 'AUTOMATION';
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
  environment: string;
  httpStatus: string;
  endpoint: string;
  dateRange: string;
}
