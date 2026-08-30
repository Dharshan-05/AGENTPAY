'use client';

import { AGMetricCard } from '@/components/ui/ag-card';

interface DeveloperMetricsProps {
  activeKeys: number;
  newKeysThisMonth: number;
  requests24h: string;
  requestsTrend: string;
  webhookDelivery: string;
  webhookEvents: number;
  activeAgents: number;
}

export function DeveloperMetrics({
  activeKeys,
  newKeysThisMonth,
  requests24h,
  requestsTrend,
  webhookDelivery,
  webhookEvents,
  activeAgents,
}: DeveloperMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
      <AGMetricCard
        label="ACTIVE API KEYS"
        value={activeKeys.toString()}
        subtext={`+${newKeysThisMonth} THIS MONTH`}
        trend={`+${newKeysThisMonth} Keys`}
        trendPositive={true}
        accentColor="text-blue-400"
      />

      <AGMetricCard
        label="API REQUESTS 24H"
        value={requests24h}
        subtext={`${requestsTrend} VS PREVIOUS 24H`}
        trend={requestsTrend}
        trendPositive={true}
        accentColor="text-emerald-400"
      />

      <AGMetricCard
        label="WEBHOOK DELIVERY"
        value={webhookDelivery}
        subtext={`${webhookEvents.toLocaleString()} EVENTS DISPATCHED`}
        trend={`${webhookDelivery} Clear`}
        trendPositive={true}
        accentColor="text-emerald-400"
      />

      <AGMetricCard
        label="ACTIVE AGENT CONNECTIONS"
        value={activeAgents.toString()}
        subtext="ZERO-TRUST VERIFIED"
        trend="mTLS Enforced"
        trendPositive={true}
        accentColor="text-blue-400"
      />
    </div>
  );
}
