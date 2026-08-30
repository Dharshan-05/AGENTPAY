export interface SourceApiKeyRecord {
  id: string;
  name: string;
  keyPrefix: string;
  created: string;
  lastUsed: string;
  scope: 'FULL_ACCESS' | 'READ_ONLY' | 'PAYMENTS_ONLY';
  environment: 'PRODUCTION' | 'SANDBOX';
  status: 'ACTIVE' | 'REVOKED';
}

export interface SourceWebhookEndpointRecord {
  id: string;
  url: string;
  events: string[];
  status: 'ACTIVE' | 'DISABLED';
  signingSecret: string;
  created: string;
}

export interface SourceDeveloperLogRecord {
  id: string;
  method: 'GET' | 'POST' | 'DELETE' | 'PUT';
  endpoint: string;
  statusCode: number;
  latency: string;
  ipAddress: string;
  timestamp: string;
}
