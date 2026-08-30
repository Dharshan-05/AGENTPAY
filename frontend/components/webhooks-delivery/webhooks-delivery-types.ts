'use client';
export type WebhooksDeliveryTabType = 'DISPATCH_LOGS' | 'RETRY_QUEUE' | 'HMAC_SIGNATURES' | 'ENDPOINT_HEALTH' | 'AUDIT';
export interface WebhooksDeliveryRecord {
  id: string;
  webhookId: string;
  eventType: string;
  targetEndpoint: string;
  httpStatus: number;
  attemptCount: number;
  latencyMs: number;
  status: 'DELIVERED' | 'FAILED_RETRYING';
}
