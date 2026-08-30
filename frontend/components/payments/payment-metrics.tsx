'use client';

import { AGMetricCard } from '@/components/ui/ag-card';

interface PaymentMetricsProps {
  grossVolume: string;
  volumeTrend: string;
  successfulPayments: number;
  successRate: string;
  failedPayments: number;
  failureRate: string;
  netPayout: string;
}

export function PaymentMetrics({
  grossVolume,
  volumeTrend,
  successfulPayments,
  successRate,
  failedPayments,
  failureRate,
  netPayout,
}: PaymentMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
      <AGMetricCard
        label="GROSS PAYMENT VOLUME"
        value={grossVolume}
        subtext={`${volumeTrend} VS LAST WEEK`}
        trend={volumeTrend}
        trendPositive={true}
        accentColor="text-emerald-400"
      />

      <AGMetricCard
        label="SUCCESSFUL PAYMENTS"
        value={successfulPayments.toLocaleString()}
        subtext={`${successRate} SUCCESS RATE`}
        trend={`${successRate} Clear`}
        trendPositive={true}
        accentColor="text-emerald-400"
      />

      <AGMetricCard
        label="FAILED / DECLINED"
        value={failedPayments.toString()}
        subtext={`${failureRate} FAILURE RATE`}
        trend={`${failureRate} Blocked`}
        trendPositive={false}
        accentColor="text-red-400"
      />

      <AGMetricCard
        label="NET PAYOUT VOLUME"
        value={netPayout}
        subtext="AFTER FEES"
        trend="T+1 Schedule"
        trendPositive={true}
        accentColor="text-blue-400"
      />
    </div>
  );
}
