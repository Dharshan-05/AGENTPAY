'use client';

import { AGMetricCard } from '@/components/ui/ag-card';

interface SourceMetricsProps {
  totalMethods: number;
  activeMethods: number;
  verifiedMethods: number;
  processorCoverage: string;
  restrictedBlocked: number;
  expiringExpired: number;
}

export function SourceMetrics({
  totalMethods,
  activeMethods,
  verifiedMethods,
  processorCoverage,
  restrictedBlocked,
  expiringExpired,
}: SourceMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 font-mono">
      <AGMetricCard
        label="PAYMENT METHODS"
        value={`${totalMethods} TOTAL`}
        subtext="REGISTERED INSTRUMENTS"
        accentColor="text-blue-400"
      />
      <AGMetricCard
        label="ACTIVE METHODS"
        value={`${activeMethods} ACTIVE`}
        subtext="AGENT-READY FOR ROUTING"
        trend="+14.2% Growth"
        trendPositive
        accentColor="text-emerald-400"
      />
      <AGMetricCard
        label="VERIFIED METHODS"
        value={`${verifiedMethods} VERIFIED`}
        subtext="AVS / 3DS / ACH CONFIRMED"
        trend="99.9% Compliance"
        trendPositive
        accentColor="text-emerald-400"
      />
      <AGMetricCard
        label="PROCESSOR COVERAGE"
        value={processorCoverage}
        subtext="STRIPE / ADYEN / JPM / CITI / RZP"
        accentColor="text-blue-400"
      />
      <AGMetricCard
        label="RESTRICTED / BLOCKED"
        value={`${restrictedBlocked} BLOCKED`}
        subtext="FRAUDGUARD & POLICY STOPS"
        trend="-1 From Yesterday"
        trendPositive
        accentColor="text-amber-400"
      />
      <AGMetricCard
        label="EXPIRING / EXPIRED"
        value={`${expiringExpired} ATTENTION`}
        subtext="TOKEN ROTATION DUE"
        accentColor="text-rose-400"
      />
    </div>
  );
}
