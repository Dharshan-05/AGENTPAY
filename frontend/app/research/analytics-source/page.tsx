'use client';

import { useState } from 'react';
import './analytics-source.css';
import { SourceHeader } from '@/components/research/analytics/source-header';
import { SourceMetrics } from '@/components/research/analytics/source-metrics';
import { SourceCharts } from '@/components/research/analytics/source-charts';
import { SourceTables } from '@/components/research/analytics/source-tables';
import { SourceInspector } from '@/components/research/analytics/source-inspector';
import {
  SourceKpiMetric,
  SourceAgentRecord,
  SourceMerchantRecord,
  SourceAnomalyRecord,
} from '@/components/research/analytics/source-types';

const MOCK_KPIS: SourceKpiMetric[] = [
  { title: 'Total Transaction Volume', value: '$4.82M', change: '+18.6%', isPositive: true, subtext: '30-Day Aggregated Financial Volume' },
  { title: 'Transaction Success Rate', value: '94.2%', change: '+2.4%', isPositive: true, subtext: 'Across 1,280 Agent Executions' },
  { title: 'Active Agents', value: '128', change: '+14 New', isPositive: true, subtext: 'Utilizing Autonomous Payment Rails' },
  { title: 'Risk Detection Rate', value: '7.8%', change: '1,482 Signals', isPositive: false, subtext: 'Flagged by Fraud Models' },
];

const MOCK_AGENTS: SourceAgentRecord[] = [
  { id: '1', name: 'Procurement Agent #892', agentId: 'AGT-892', transactions: 428, successRate: '97.8%', avgRisk: 0.08, policyViolations: 3, totalValue: '$842,420', status: 'AUTHORIZED' },
  { id: '2', name: 'Shopping Agent #441', agentId: 'AGT-441', transactions: 312, successRate: '92.4%', avgRisk: 0.42, policyViolations: 12, totalValue: '$428,920', status: 'REVIEW' },
  { id: '3', name: 'Travel Agent #118', agentId: 'AGT-118', transactions: 198, successRate: '95.6%', avgRisk: 0.17, policyViolations: 4, totalValue: '$182,430', status: 'AUTHORIZED' },
];

const MOCK_MERCHANTS: SourceMerchantRecord[] = [
  { name: 'Acme Hardware Corp', category: 'Hardware / GPUs', volume: '$842,420', riskScore: 18, successRate: '98.2%', status: 'AUTHORIZED' },
  { name: 'ElectroHub Direct', category: 'Components', volume: '$428,920', riskScore: 48, successRate: '94.0%', status: 'AUTHORIZED' },
  { name: 'United Airlines', category: 'Travel', volume: '$182,430', riskScore: 12, successRate: '96.5%', status: 'AUTHORIZED' },
  { name: 'Offshore Wire Gateway', category: 'Financial Services', volume: '$14,800', riskScore: 96, successRate: '0.0%', status: 'BLOCKED' },
];

const MOCK_ANOMALIES: SourceAnomalyRecord[] = [
  { id: 'an-1', title: 'Unusual Transaction Velocity', severity: 'HIGH', agent: 'Procurement Agent #892', agentId: 'AGT-892', riskScore: 91, timestamp: '02:14:18 UTC', status: 'INVESTIGATING' },
  { id: 'an-2', title: 'Device Identity Collision', severity: 'HIGH', agent: 'Shopping Agent #441', agentId: 'AGT-441', riskScore: 87, timestamp: '02:04:22 UTC', status: 'REVIEW' },
  { id: 'an-3', title: 'Merchant Category Deviation', severity: 'MEDIUM', agent: 'Travel Agent #118', agentId: 'AGT-118', riskScore: 62, timestamp: '01:44:11 UTC', status: 'MONITORED' },
];

export default function AnalyticsSourceResearchPage() {
  const [dateRange, setDateRange] = useState<string>('24H');
  const [selectedItem, setSelectedItem] = useState<SourceAgentRecord | null>(null);

  return (
    <div className="analytics-source-root min-h-screen p-6 space-y-6 bg-slate-100 font-sans">
      
      {/* HEADER */}
      <SourceHeader
        dateRange={dateRange}
        onDateRangeChange={setDateRange}
        onRefresh={() => {}}
        onExport={() => {}}
      />

      {/* KPI METRICS */}
      <SourceMetrics metrics={MOCK_KPIS} />

      {/* CHARTS & RISK */}
      <SourceCharts />

      {/* TABLES */}
      <SourceTables
        agents={MOCK_AGENTS}
        merchants={MOCK_MERCHANTS}
        anomalies={MOCK_ANOMALIES}
        onSelectRow={(item) => setSelectedItem(item)}
      />

      {/* DRILL-DOWN INSPECTOR */}
      <SourceInspector
        item={selectedItem}
        onClose={() => setSelectedItem(null)}
      />

    </div>
  );
}
