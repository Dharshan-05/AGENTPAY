'use client';

import { AGMetricCard } from '@/components/ui/ag-card';

interface ReconciliationMetricsProps {
  totalSettled24h: string;
  activeDisputesCount: number;
  unresolvedVariancesCount: number;
  disputeWinRate: string;
}

export function ReconciliationMetrics({
  totalSettled24h,
  activeDisputesCount,
  unresolvedVariancesCount,
  disputeWinRate,
}: ReconciliationMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
      <AGMetricCard
        label="TOTAL SETTLED — 24H"
        value={totalSettled24h}
        subtext="+18.6% VS PREVIOUS PERIOD"
        trend="+18.6%"
        trendPositive={true}
        accentColor="text-emerald-400"
      />

      <AGMetricCard
        label="ACTIVE DISPUTES"
        value={activeDisputesCount.toString()}
        subtext="12 HIGH PRIORITY DOSSIERS"
        trend="42 Under Review"
        trendPositive={false}
        accentColor="text-red-400"
      />

      <AGMetricCard
        label="UNRESOLVED VARIANCES"
        value={unresolvedVariancesCount.toString()}
        subtext="$38.4K EXPOSURE"
        trend="$38.4K Exposure"
        trendPositive={false}
        accentColor="text-amber-400"
      />

      <AGMetricCard
        label="DISPUTE WIN RATE"
        value={disputeWinRate}
        subtext="+4.2% VS PREVIOUS PERIOD"
        trend="+4.2%"
        trendPositive={true}
        accentColor="text-blue-400"
      />
    </div>
  );
}
