'use client';

import { AGMetricCard } from '@/components/ui/ag-card';

interface TransactionMetricsProps {
  intentCount: number;
  txnCount: number;
  failedCount: number;
  refundCount: number;
}

export function TransactionMetrics({
  intentCount,
  txnCount,
  failedCount,
  refundCount,
}: TransactionMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 font-mono">
      <AGMetricCard
        label="PAYMENT INTENTS"
        value={`${intentCount} TOTAL`}
        subtext="ACTIVE LIFECYCLE CHAINS"
        accentColor="text-blue-400"
      />

      <AGMetricCard
        label="TRANSACTIONS 24H"
        value={`${txnCount} PROCESSED`}
        subtext="AVG LATENCY: 189MS"
        trend="+8.4% Volume"
        trendPositive={true}
        accentColor="text-emerald-400"
      />

      <AGMetricCard
        label="AUTHORIZED VOLUME"
        value="$823,769"
        subtext="99.94% AUTH RATE"
        trend="+2.1% Rate"
        trendPositive={true}
        accentColor="text-emerald-400"
      />

      <AGMetricCard
        label="CAPTURED VOLUME"
        value="$781,680"
        subtext="NET: $776,831 AFTER FEES"
        accentColor="text-blue-400"
      />

      <AGMetricCard
        label="FAILED / BLOCKED"
        value={`${failedCount} BLOCKED`}
        subtext="POLICY + RISK STOPS"
        trend="-1 From Yesterday"
        trendPositive={true}
        accentColor="text-red-400"
      />

      <AGMetricCard
        label="REFUNDS"
        value={`${refundCount} ISSUED`}
        subtext="$2,520.00 REFUNDED"
        trend="0.14% Refund Ratio"
        trendPositive={true}
        accentColor="text-amber-400"
      />
    </div>
  );
}
