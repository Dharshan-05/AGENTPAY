'use client';

import { AGMetricCard } from '@/components/ui/ag-card';

interface AgentMetricsProps {
  registeredAgentsCount: number;
  activeAgentsCount: number;
  executions24h: string;
  suspendedCount: number;
  rotationsDueCount: number;
}

export function AgentMetrics({
  registeredAgentsCount,
  activeAgentsCount,
  executions24h,
  suspendedCount,
  rotationsDueCount,
}: AgentMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
      <AGMetricCard
        label="REGISTERED AGENTS"
        value={`${registeredAgentsCount} TOTAL`}
        subtext={`${activeAgentsCount} ACTIVE IN PRODUCTION`}
        trend="100% Zero-Trust Verified"
        trendPositive={true}
        accentColor="text-emerald-400"
      />

      <AGMetricCard
        label="EXECUTIONS 24H"
        value={executions24h}
        subtext="AVG LATENCY: 142MS"
        trend="+14.2% Run Volume"
        trendPositive={true}
        accentColor="text-blue-400"
      />

      <AGMetricCard
        label="SUSPENDED / ALERTS"
        value={`${suspendedCount} SUSPENDED`}
        subtext="POLICY VARIANCE BREACH"
        trend="1 Alert Pending Review"
        trendPositive={false}
        accentColor="text-amber-400"
      />

      <AGMetricCard
        label="CREDENTIAL ROTATION"
        value={`${rotationsDueCount} ROTATIONS DUE`}
        subtext="mTLS CERTS ENFORCED"
        trend="Rotation Compliant"
        trendPositive={true}
        accentColor="text-purple-400"
      />
    </div>
  );
}
