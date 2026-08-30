'use client';

import { AGMetricCard } from '@/components/ui/ag-card';

interface AnalyticsMetricsProps {
  totalVolume: string;
  volumeTrend: string;
  successRate: string;
  successImprovement: string;
  activeAgents: number;
  newAgents: number;
  riskDetectionRate: string;
  signalsCount: number;
}

export function AnalyticsMetrics({
  totalVolume,
  volumeTrend,
  successRate,
  successImprovement,
  activeAgents,
  newAgents,
  riskDetectionRate,
  signalsCount,
}: AnalyticsMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
      <AGMetricCard
        label="TOTAL TRANSACTION VOLUME"
        value={totalVolume}
        subtext={`${volumeTrend} VS PREVIOUS PERIOD`}
        trend={volumeTrend}
        trendPositive={true}
        accentColor="text-emerald-400"
      />

      <AGMetricCard
        label="TRANSACTION SUCCESS RATE"
        value={successRate}
        subtext={`${successImprovement} IMPROVEMENT`}
        trend={successImprovement}
        trendPositive={true}
        accentColor="text-emerald-400"
      />

      <AGMetricCard
        label="ACTIVE AGENTS"
        value={activeAgents.toString()}
        subtext={`+${newAgents} THIS PERIOD`}
        trend={`+${newAgents} New`}
        trendPositive={true}
        accentColor="text-blue-400"
      />

      <AGMetricCard
        label="RISK DETECTION RATE"
        value={riskDetectionRate}
        subtext={`${signalsCount.toLocaleString()} SIGNALS DETECTED`}
        trend={`${signalsCount} Signals`}
        trendPositive={false}
        accentColor="text-amber-400"
      />
    </div>
  );
}
