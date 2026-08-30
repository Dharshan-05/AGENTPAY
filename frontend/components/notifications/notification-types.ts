'use client';
export type NotificationsTabType = 'DELIVERIES' | 'WEBHOOK_RETRIES' | 'EMAIL' | 'SMS' | 'FAILURE_ALERTS' | 'TEMPLATES' | 'AUDIT';
export interface NotificationRecord {
  id: string;
  notificationId: string;
  event: string;
  channel: 'WEBHOOK' | 'EMAIL' | 'SMS' | 'SLACK';
  target: string;
  status: 'DELIVERED' | 'RETRYING' | 'FAILED';
  latencyMs: number;
  timestamp: string;
}
