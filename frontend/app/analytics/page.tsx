'use client';

import { useState } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { AnalyticsHeader } from '@/components/analytics/analytics-header';
import { AnalyticsMetrics } from '@/components/analytics/analytics-metrics';
import { AnalyticsControls } from '@/components/analytics/analytics-controls';
import { TransactionTelemetry } from '@/components/analytics/transaction-telemetry';
import { RiskIntelligence } from '@/components/analytics/risk-intelligence';
import { AgentPerformance } from '@/components/analytics/agent-performance';
import { PolicyAnalytics } from '@/components/analytics/policy-analytics';
import { FraudAnalytics } from '@/components/analytics/fraud-analytics';
import { MerchantAnalytics } from '@/components/analytics/merchant-analytics';
import { RegionalAnalytics } from '@/components/analytics/regional-analytics';
import { AnomalyDetection } from '@/components/analytics/anomaly-detection';
import { AnalyticsEvents } from '@/components/analytics/analytics-events';
import { AIInsights } from '@/components/analytics/ai-insights';
import { AnalyticsInspector } from '@/components/analytics/analytics-inspector';

import {
  AgentPerformanceRecord,
  PolicyTriggerRecord,
  FraudSignalRecord,
  MerchantCategoryRecord,
  RegionalActivityRecord,
  AnomalyRecord,
  AnalyticsEventRecord,
} from '@/components/analytics/analytics-types';

const MOCK_AGENTS: AgentPerformanceRecord[] = [
  {
    agentName: 'Procurement Agent #892',
    agentId: 'AGT-892',
    transactions: 428,
    successRate: '97.8%',
    avgRisk: 0.08,
    policyViolations: 3,
    totalValue: '$842,420',
    decision: 'AUTHORIZED',
  },
  {
    agentName: 'Shopping Agent #441',
    agentId: 'AGT-441',
    transactions: 312,
    successRate: '92.4%',
    avgRisk: 0.42,
    policyViolations: 12,
    totalValue: '$428,920',
    decision: 'REVIEW',
  },
  {
    agentName: 'Travel Agent #118',
    agentId: 'AGT-118',
    transactions: 198,
    successRate: '95.6%',
    avgRisk: 0.17,
    policyViolations: 4,
    totalValue: '$182,430',
    decision: 'AUTHORIZED',
  },
];

const MOCK_POLICIES: PolicyTriggerRecord[] = [
  { code: 'AGP-GOV-001', name: 'Spend Governance', evaluations: 6420, triggered: 142, blockRate: '2.2%' },
  { code: 'AGP-TXN-002', name: 'Transaction Velocity', evaluations: 4810, triggered: 98, blockRate: '2.0%' },
  { code: 'AGP-MER-003', name: 'Merchant Restrictions', evaluations: 3200, triggered: 84, blockRate: '2.6%' },
  { code: 'AGP-DATA-004', name: 'Sensitive Data Shield', evaluations: 2150, triggered: 42, blockRate: '1.9%' },
  { code: 'AGP-AUTH-005', name: 'Human Approval Required', evaluations: 1200, triggered: 68, blockRate: '5.6%' },
  { code: 'AGP-RISK-006', name: 'Risk Threshold Auth', evaluations: 712, triggered: 48, blockRate: '6.7%' },
];

const MOCK_SIGNALS: FraudSignalRecord[] = [
  { name: 'Synthetic Identity Velocity', count: 482, severity: 'HIGH', contribution: 35 },
  { name: 'Device Fingerprint Collision', count: 341, severity: 'HIGH', contribution: 28 },
  { name: 'GeoIP Mismatch', count: 289, severity: 'MEDIUM', contribution: 18 },
  { name: 'High-Frequency API Burst', count: 210, severity: 'MEDIUM', contribution: 12 },
  { name: 'Unusual Agent Behavior', count: 160, severity: 'LOW', contribution: 7 },
];

const MOCK_MERCHANTS: MerchantCategoryRecord[] = [
  { merchant: 'Acme Hardware Corp', category: 'Equipment / GPUs', volume: '$842,420', riskScore: 18, successRate: '98.2%', decision: 'AUTHORIZED' },
  { merchant: 'ElectroHub Direct', category: 'Hardware Components', volume: '$428,920', riskScore: 48, successRate: '94.0%', decision: 'AUTHORIZED' },
  { merchant: 'United Airlines', category: 'Corporate Travel', volume: '$182,430', riskScore: 12, successRate: '96.5%', decision: 'AUTHORIZED' },
  { merchant: 'Offshore Wire Gateway', category: 'Financial Services', volume: '$14,800', riskScore: 96, successRate: '0.0%', decision: 'BLOCKED' },
];

const MOCK_REGIONS: RegionalActivityRecord[] = [
  { region: 'North America', code: 'US', volume: '$2.84M', transactions: 780, riskIndex: 14, successRate: '96.8%' },
  { region: 'Europe', code: 'EU', volume: '$1.12M', transactions: 320, riskIndex: 18, successRate: '95.2%' },
  { region: 'Asia-Pacific', code: 'APAC', volume: '$540K', transactions: 140, riskIndex: 22, successRate: '93.5%' },
  { region: 'India', code: 'INDIA', volume: '$220K', transactions: 80, riskIndex: 16, successRate: '94.8%' },
  { region: 'Middle East', code: 'ME', volume: '$100K', transactions: 24, riskIndex: 28, successRate: '91.2%' },
];

const MOCK_ANOMALIES: AnomalyRecord[] = [
  { anomaly: 'Unusual Transaction Velocity', severity: 'HIGH', agent: 'Procurement Agent #892', agentId: 'AGT-892', riskScore: 91, detectedAt: '02:14:18 UTC', status: 'INVESTIGATING' },
  { anomaly: 'Device Identity Collision', severity: 'HIGH', agent: 'Shopping Agent #441', agentId: 'AGT-441', riskScore: 87, detectedAt: '02:04:22 UTC', status: 'REVIEW' },
  { anomaly: 'Merchant Category Deviation', severity: 'MEDIUM', agent: 'Travel Agent #118', agentId: 'AGT-118', riskScore: 62, detectedAt: '01:44:11 UTC', status: 'MONITORED' },
];

const MOCK_EVENTS: AnalyticsEventRecord[] = [
  { id: 'evt_an1', type: 'ANALYTICS.TRANSACTION', agent: 'AGT-892', riskScore: 18, timestamp: '02:14:22 UTC', status: 'DELIVERED' },
  { id: 'evt_an2', type: 'ANALYTICS.RISK_UPDATE', agent: 'AGT-441', riskScore: 48, timestamp: '02:10:18 UTC', status: 'PROCESSED' },
  { id: 'evt_an3', type: 'ANALYTICS.POLICY_TRIGGER', agent: 'AGT-203', riskScore: 96, timestamp: '01:58:44 UTC', status: 'FLAGGED' },
  { id: 'evt_an4', type: 'ANALYTICS.ANOMALY_DETECTED', agent: 'AGT-118', riskScore: 62, timestamp: '01:44:11 UTC', status: 'PROCESSED' },
];

export default function ProductionAnalyticsPage() {
  const [dateRange, setDateRange] = useState<string>('24H');
  const [selectedAgent, setSelectedAgent] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [riskBand, setRiskBand] = useState<string>('ALL');
  const [merchantFilter, setMerchantFilter] = useState<string>('ALL');
  const [regionFilter, setRegionFilter] = useState<string>('ALL');

  // Inspector state
  const [selectedAgentRecord, setSelectedAgentRecord] = useState<AgentPerformanceRecord | null>(null);
  const [selectedAnomalyRecord, setSelectedAnomalyRecord] = useState<AnomalyRecord | null>(null);

  const handleResetFilters = () => {
    setDateRange('24H');
    setSelectedAgent('ALL');
    setStatusFilter('ALL');
    setRiskBand('ALL');
    setMerchantFilter('ALL');
    setRegionFilter('ALL');
  };

  return (
    <AgentPayShell activeTab="analytics">
      <div className="space-y-6 pb-12">
        
        {/* PAGE HEADER */}
        <AnalyticsHeader
          onRefresh={() => {}}
          onExport={() => {}}
          onGenerateReport={() => {}}
        />

        {/* KPI TELEMETRY CARDS */}
        <AnalyticsMetrics
          totalVolume="$4.82M"
          volumeTrend="+18.6%"
          successRate="94.2%"
          successImprovement="+2.4%"
          activeAgents={128}
          newAgents={14}
          riskDetectionRate="7.8%"
          signalsCount={1482}
        />

        {/* ANALYTICS CONTROL BAR */}
        <AnalyticsControls
          dateRange={dateRange}
          onDateRangeChange={setDateRange}
          selectedAgent={selectedAgent}
          onAgentChange={setSelectedAgent}
          statusFilter={statusFilter}
          onStatusChange={setStatusFilter}
          riskBand={riskBand}
          onRiskBandChange={setRiskBand}
          merchantFilter={merchantFilter}
          onMerchantChange={setMerchantFilter}
          regionFilter={regionFilter}
          onRegionChange={setRegionFilter}
          onReset={handleResetFilters}
        />

        {/* PRIMARY ANALYTICS & RISK INTELLIGENCE (2 COLUMNS) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <TransactionTelemetry />
          </div>
          <div>
            <RiskIntelligence />
          </div>
        </div>

        {/* AGENT PERFORMANCE TELEMETRY */}
        <div className="cursor-pointer" onClick={() => setSelectedAgentRecord(MOCK_AGENTS[0])}>
          <AgentPerformance agents={MOCK_AGENTS} />
        </div>

        {/* POLICY & FRAUD INTELLIGENCE (2 COLUMNS) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PolicyAnalytics policies={MOCK_POLICIES} />
          <FraudAnalytics signals={MOCK_SIGNALS} />
        </div>

        {/* MERCHANT & REGIONAL INTELLIGENCE (2 COLUMNS) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <MerchantAnalytics merchants={MOCK_MERCHANTS} />
          </div>
          <div>
            <RegionalAnalytics regions={MOCK_REGIONS} />
          </div>
        </div>

        {/* ANOMALY DETECTION & LIVE EVENT STREAM (2 COLUMNS) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 cursor-pointer" onClick={() => setSelectedAnomalyRecord(MOCK_ANOMALIES[0])}>
            <AnomalyDetection anomalies={MOCK_ANOMALIES} />
          </div>
          <div>
            <AnalyticsEvents events={MOCK_EVENTS} />
          </div>
        </div>

        {/* AI ANALYTICS INSIGHTS */}
        <AIInsights />

        {/* ANALYTICS DRILL-DOWN INSPECTOR DRAWER */}
        <AnalyticsInspector
          agentItem={selectedAgentRecord}
          anomalyItem={selectedAnomalyRecord}
          onClose={() => {
            setSelectedAgentRecord(null);
            setSelectedAnomalyRecord(null);
          }}
        />

      </div>
    </AgentPayShell>
  );
}
