'use client';

import { AGMetricCard } from '@/components/ui/ag-card';

interface PaymentMethodMetricsProps {
  totalMethods: number;
  activeMethods: number;
  methodsUsed24h: number;
  authSuccessRate: string;
  highRiskCount: number;
  suspendedCount: number;
}

export function PaymentMethodMetrics({
  totalMethods,
  activeMethods,
  methodsUsed24h,
  authSuccessRate,
  highRiskCount,
  suspendedCount,
}: PaymentMethodMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 font-mono">
      <AGMetricCard
        label="PAYMENT METHODS"
        value={`${totalMethods}`}
        subtext="REGISTERED INSTRUMENTS"
        accentColor="text-blue-400"
      />
      <AGMetricCard
        label="ACTIVE METHODS"
        value={`${activeMethods}`}
        subtext="READY FOR AGENT ROUTING"
        trend="+14.2% Growth"
        trendPositive
        accentColor="text-emerald-400"
      />
      <AGMetricCard
        label="METHODS USED 24H"
        value={methodsUsed24h.toLocaleString()}
        subtext="LAST 24H EXECUTIONS"
        trend="+4.8% Volume"
        trendPositive
        accentColor="text-emerald-400"
      />
      <AGMetricCard
        label="AUTH SUCCESS RATE"
        value={authSuccessRate}
        subtext="LIVE CONNECTOR SLA"
        trend="+0.12% Rate"
        trendPositive
        accentColor="text-blue-400"
      />
      <AGMetricCard
        label="HIGH-RISK METHODS"
        value={highRiskCount.toString().padStart(2, '0')}
        subtext="ELEVATED FRAUDGUARD SCORE"
        trend="-1 From Yesterday"
        trendPositive
        accentColor="text-amber-400"
      />
      <AGMetricCard
        label="SUSPENDED METHODS"
        value={suspendedCount.toString().padStart(2, '0')}
        subtext="POLICY / SECURITY STOPS"
        accentColor="text-rose-400"
      />
    </div>
  );
}
