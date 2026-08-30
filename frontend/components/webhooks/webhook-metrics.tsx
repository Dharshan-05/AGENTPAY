'use client';

import { AGMetricCard } from '@/components/ui/ag-card';

interface WebhookMetricsProps {
  endpointCount: number;
  deliveryCount: number;
  successRate: string;
  p95Latency: string;
  failedCount: number;
  deadLetterCount: number;
}

export function WebhookMetrics({
  endpointCount,
  deliveryCount,
  successRate,
  p95Latency,
  failedCount,
  deadLetterCount,
}: WebhookMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 font-mono">
      <AGMetricCard
        label="ENDPOINTS"
        value={`${endpointCount} ACTIVE`}
        subtext="REGISTERED WEBHOOK RECEIVERS"
        accentColor="text-blue-400"
      />
      <AGMetricCard
        label="DELIVERIES 24H"
        value={deliveryCount.toLocaleString()}
        subtext="TOTAL DISPATCHED EVENTS"
        trend="+12.4% Volume"
        trendPositive
        accentColor="text-emerald-400"
      />
      <AGMetricCard
        label="SUCCESS RATE"
        value={successRate}
        subtext="HMAC VERIFIED DELIVERIES"
        trend="+0.04% SLA"
        trendPositive
        accentColor="text-emerald-400"
      />
      <AGMetricCard
        label="P95 LATENCY"
        value={p95Latency}
        subtext="DISPATCH TO ACK TIME"
        accentColor="text-blue-400"
      />
      <AGMetricCard
        label="FAILED / RETRYING"
        value={`${failedCount} QUEUED`}
        subtext="EXPONENTIAL BACKOFF QUEUE"
        trend="-3 From Yesterday"
        trendPositive
        accentColor="text-amber-400"
      />
      <AGMetricCard
        label="DEAD-LETTER QUEUE"
        value={`${deadLetterCount} EXHAUSTED`}
        subtext="MANUAL REPLAY REQUIRED"
        accentColor="text-rose-400"
      />
    </div>
  );
}
