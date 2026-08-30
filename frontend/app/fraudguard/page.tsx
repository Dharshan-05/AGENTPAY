'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGCard, AGMetricCard, AGGlassCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { AGDrawer } from '@/components/ui/ag-drawer';
import {
  Cpu,
  ShieldAlert,
  Search,
  Filter,
  Activity,
  AlertTriangle,
  FileText,
  UserCheck,
  CheckCircle2,
  XCircle,
  Clock,
  ChevronRight,
  TrendingUp,
  Sliders,
  Database,
  BarChart3,
  Lock,
  ArrowRight,
  Radio,
  Share2,
  Brain,
  Shield,
  Layers,
  Sparkles,
  RefreshCw,
  Download,
  Plus,
  Send,
  MessageSquare,
} from 'lucide-react';

interface SignalContribution {
  name: string;
  score: number;
}

interface FraudCase {
  id: string;
  agentName: string;
  agentId: string;
  transactionId: string;
  amount: string;
  merchant: string;
  category: string;
  riskScore: number;
  riskBand: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  topSignal: string;
  decision: 'AUTHORIZED' | 'PENDING REVIEW' | 'BLOCKED';
  timestamp: string;
  ipAddress: string;
  deviceFingerprint: string;
  geoLocation: string;
  policyMatched: string;
  policyResult: string;
  categoryContributions: {
    identity: number;
    velocity: number;
    behavioral: number;
    financial: number;
    agent: number;
  };
  explainability: SignalContribution[];
  aiBrief: string;
  notes: { author: string; time: string; text: string }[];
}

const INITIAL_QUEUE: FraudCase[] = [
  {
    id: 'CASE-8921',
    agentName: 'Procurement Agent #892',
    agentId: 'AGT-892',
    transactionId: 'TXN-8F21A',
    amount: '$7,820.00',
    merchant: 'Acme Hardware',
    category: 'Electronics / GPU',
    riskScore: 84,
    riskBand: 'HIGH',
    topSignal: 'Synthetic Identity Velocity',
    decision: 'PENDING REVIEW',
    timestamp: '02:04:18 UTC',
    ipAddress: '103.14.88.19 (Frankfurt Node)',
    deviceFingerprint: 'dfp-webgl-991177 (Collision Match)',
    geoLocation: 'Frankfurt, DE (Billing Mismatch)',
    policyMatched: 'AGP-RISK-006 (Anomaly Threshold)',
    policyResult: 'HUMAN_REVIEW_REQUIRED',
    categoryContributions: { identity: 35, velocity: 28, behavioral: 18, financial: 12, agent: 0 },
    explainability: [
      { name: 'Synthetic Identity Velocity', score: 35 },
      { name: 'Device Collision', score: 28 },
      { name: 'Geo Mismatch', score: 18 },
      { name: 'Transaction Velocity', score: 12 },
      { name: 'Trusted Merchant', score: -8 },
    ],
    aiBrief:
      'Transaction exhibits elevated synthetic identity and device-collision signals. Agent velocity exceeds normal behavioral baseline. AGENTGUARD policy AGP-RISK-006 recommends manual review.',
    notes: [
      { author: 'SIU Lead', time: '02:10:00 UTC', text: 'Flagged for high synthetic identity score and WebGL fingerprint collision.' },
    ],
  },
  {
    id: 'CASE-4412',
    agentName: 'Shopping Agent #441',
    agentId: 'AGT-441',
    transactionId: 'TXN-9C81B',
    amount: '$1,240.00',
    merchant: 'ElectroHub',
    category: 'Hardware',
    riskScore: 48,
    riskBand: 'MEDIUM',
    topSignal: 'New Merchant First-Seen',
    decision: 'AUTHORIZED',
    timestamp: '02:04:22 UTC',
    ipAddress: '198.51.100.42 (US-East Node)',
    deviceFingerprint: 'dfp-webgl-441088 (Unique)',
    geoLocation: 'New York, US',
    policyMatched: 'AGP-TXN-002 (Spend Cap)',
    policyResult: 'AUTO_PASSED',
    categoryContributions: { identity: 10, velocity: 14, behavioral: 10, financial: 8, agent: 6 },
    explainability: [
      { name: 'New Merchant First-Seen', score: 24 },
      { name: 'Category Drift', score: 14 },
      { name: 'Verified Agent Token', score: -10 },
    ],
    aiBrief:
      'First-time transaction with ElectroHub. Spend is within daily limit ($1,240 / $5,000). Risk cleared for automatic authorization.',
    notes: [],
  },
  {
    id: 'CASE-2039',
    agentName: 'Logistics Agent #203',
    agentId: 'AGT-203',
    transactionId: 'TXN-2A91D',
    amount: '$14,800.00',
    merchant: 'Unknown Gateway',
    category: 'Wire Transfer',
    riskScore: 96,
    riskBand: 'CRITICAL',
    topSignal: 'Unverified Overseas Wire Gateway',
    decision: 'BLOCKED',
    timestamp: '02:04:27 UTC',
    ipAddress: '45.142.214.8 (Offshore Proxy)',
    deviceFingerprint: 'dfp-webgl-000881 (Blacklisted)',
    geoLocation: 'Panama City, PA',
    policyMatched: 'AGP-MER-003 (Sanction Shield)',
    policyResult: 'EMERGENCY_BLOCK',
    categoryContributions: { identity: 35, velocity: 30, behavioral: 20, financial: 15, agent: 0 },
    explainability: [
      { name: 'Unverified Wire Gateway', score: 40 },
      { name: 'Hardened Credential Leak', score: 32 },
      { name: 'Offshore Proxy IP', score: 18 },
      { name: 'Unsanctioned Beneficiary', score: 14 },
    ],
    aiBrief:
      'Critical risk breach detected. Transaction routed through unverified offshore wire gateway with blacklisted device fingerprint. Immediate automated block enforced.',
    notes: [
      { author: 'Automated Shield', time: '02:04:27 UTC', text: 'Blocked by AGP-MER-003 zero-trust enforcement rule.' },
    ],
  },
  {
    id: 'CASE-1184',
    agentName: 'Travel Agent #118',
    agentId: 'AGT-118',
    transactionId: 'TXN-7B12E',
    amount: '$1,820.00',
    merchant: 'United Airlines',
    category: 'Corporate Travel',
    riskScore: 18,
    riskBand: 'LOW',
    topSignal: 'Verified Corporate Domain',
    decision: 'AUTHORIZED',
    timestamp: '01:58:10 UTC',
    ipAddress: '12.180.44.12 (Corporate VPN)',
    deviceFingerprint: 'dfp-webgl-118002 (Verified)',
    geoLocation: 'Austin, TX, US',
    policyMatched: 'AGP-GOV-001 (Travel Cap)',
    policyResult: 'AUTO_PASSED',
    categoryContributions: { identity: 5, velocity: 0, behavioral: 0, financial: 13, agent: 0 },
    explainability: [
      { name: 'Verified Corporate Domain', score: -12 },
      { name: 'Pre-Approved Travel MCC', score: -10 },
      { name: 'Standard Flight Amount', score: 8 },
    ],
    aiBrief:
      'Standard corporate flight booking for SecOps Summit. Pre-approved MCC code and clean corporate IP reputation score.',
    notes: [],
  },
];

export default function FraudGuardProductionPage() {
  const [queue, setQueue] = useState<FraudCase[]>(INITIAL_QUEUE);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'1H' | '24H' | '7D'>('24H');

  // Filters
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [decisionFilter, setDecisionFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Drawer Notes State
  const [newNoteText, setNewNoteText] = useState<string>('');

  // Selected Case Object
  const selectedCase = useMemo(
    () => queue.find((c) => c.id === selectedCaseId) || null,
    [queue, selectedCaseId]
  );

  // Filtered Queue
  const filteredQueue = useMemo(() => {
    return queue.filter((c) => {
      if (riskFilter !== 'ALL' && c.riskBand !== riskFilter) return false;
      if (decisionFilter !== 'ALL' && c.decision !== decisionFilter) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        return (
          c.id.toLowerCase().includes(q) ||
          c.agentName.toLowerCase().includes(q) ||
          c.merchant.toLowerCase().includes(q) ||
          c.topSignal.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [queue, riskFilter, decisionFilter, searchQuery]);

  // Handle Investigator Verdict Updates
  const handleUpdateVerdict = (caseId: string, verdict: 'AUTHORIZED' | 'PENDING REVIEW' | 'BLOCKED') => {
    setQueue((prev) =>
      prev.map((item) => (item.id === caseId ? { ...item, decision: verdict } : item))
    );
  };

  // Handle Add Note
  const handleAddNote = () => {
    if (!selectedCaseId || !newNoteText.trim()) return;
    const text = newNoteText.trim();
    setQueue((prev) =>
      prev.map((item) => {
        if (item.id === selectedCaseId) {
          return {
            ...item,
            notes: [
              ...item.notes,
              { author: 'Investigator (You)', time: new Date().toLocaleTimeString() + ' UTC', text },
            ],
          };
        }
        return item;
      })
    );
    setNewNoteText('');
  };

  return (
    <AgentPayShell activeTab="fraudguard">
      <div className="space-y-6 pb-12">
        
        {/* MASTER PAGE HEADER */}
        <PageHeader
          eyebrow="AI RISK INTELLIGENCE & EXPLAINABLE RISK CONTROL"
          title="FRAUD"
          highlightTitle="GUARD"
          description="Autonomous agent transaction risk scoring, real-time behavioral anomaly detection, explainable SHAP vectors, and investigator control."
          icon={Cpu}
          statusBadge={
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              FRAUD ENGINE ONLINE (v1.0)
            </span>
          }
          actions={
            <>
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-white/[0.06] font-mono text-xs text-slate-300">
                <span>MODEL:</span>
                <span className="text-blue-400 font-bold">FRAUDGUARD-XGB</span>
              </div>
              <AGButton variant="ghost" size="md" icon={RefreshCw}>
                Refresh Feed
              </AGButton>
              <AGButton variant="primary" size="md" icon={Download}>
                Export Audit Logs
              </AGButton>
            </>
          }
        />

        {/* 4 MASTER AGENTPAY KPI CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard
            label="HIGH RISK QUEUE"
            value="12"
            subtext="Cases requiring immediate investigation"
            trend="+2 Pending"
            trendPositive={false}
            accentColor="text-amber-400"
          />

          <AGMetricCard
            label="AVG RISK SCORE"
            value="56.4 / 100"
            subtext="24h Aggregated Anomaly Index"
            trend="Live Index"
            trendPositive={true}
            accentColor="text-slate-100"
          />

          <AGMetricCard
            label="SIGNAL TRIGGERS"
            value="1,482"
            subtext="24h detected anomalies"
            trend="30 Rules Active"
            trendPositive={true}
            accentColor="text-emerald-400"
          />

          <AGMetricCard
            label="RESOLUTION RATE"
            value="94.2%"
            subtext="AI-assisted resolution"
            trend="82% Automated"
            trendPositive={true}
            accentColor="text-blue-400"
          />
        </div>

        {/* MAIN INTELLIGENCE AREA (2-COLUMN LAYOUT) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* LEFT 2 COLS: RISK INTELLIGENCE TELEMETRY CHART */}
          <div className="lg:col-span-2 space-y-4">
            <AGCard className="space-y-4">
              <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] font-mono text-xs gap-3">
                <div className="flex items-center gap-2 font-bold text-slate-100">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  <span>RISK INTELLIGENCE TELEMETRY</span>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-white/10 text-[10px]">
                    {(['1H', '24H', '7D'] as const).map((r) => (
                      <button
                        key={r}
                        onClick={() => setTimeRange(r)}
                        className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                          timeRange === r
                            ? 'bg-emerald-500 text-slate-950 shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                            : 'text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        {r}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Chart SVG Visualization */}
              <div className="h-60 rounded-xl bg-slate-950/90 border border-white/[0.04] p-4 flex flex-col justify-between font-mono text-xs relative overflow-hidden">
                <div className="flex justify-between items-center text-[10px] text-slate-500">
                  <span>Payment Risk (Emerald) · Agent Risk (Blue) · Behavioral Anomaly (Purple)</span>
                  <span>Live Stream</span>
                </div>

                <div className="h-40 w-full flex items-end justify-between gap-3 pt-4">
                  {[
                    { pay: 25, agent: 15, beh: 10 },
                    { pay: 40, agent: 25, beh: 18 },
                    { pay: 55, agent: 35, beh: 22 },
                    { pay: 75, agent: 50, beh: 35 },
                    { pay: 84, agent: 62, beh: 48 },
                    { pay: 60, agent: 45, beh: 30 },
                    { pay: 35, agent: 20, beh: 15 },
                    { pay: 92, agent: 78, beh: 65 },
                    { pay: 48, agent: 32, beh: 20 },
                    { pay: 68, agent: 52, beh: 38 },
                  ].map((d, idx) => (
                    <div key={idx} className="flex-1 flex items-end justify-center gap-1 h-full">
                      <div
                        className="w-1/3 bg-emerald-500/80 rounded-t hover:bg-emerald-400 transition-colors"
                        style={{ height: `${d.pay}%` }}
                        title={`Payment Risk: ${d.pay}%`}
                      />
                      <div
                        className="w-1/3 bg-blue-500/80 rounded-t hover:bg-blue-400 transition-colors"
                        style={{ height: `${d.agent}%` }}
                        title={`Agent Risk: ${d.agent}%`}
                      />
                      <div
                        className="w-1/3 bg-purple-500/80 rounded-t hover:bg-purple-400 transition-colors"
                        style={{ height: `${d.beh}%` }}
                        title={`Behavioral Anomaly: ${d.beh}%`}
                      />
                    </div>
                  ))}
                </div>

                {/* Legend Footer */}
                <div className="flex items-center justify-between text-[10px] pt-2 border-t border-white/[0.06] text-slate-400">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded bg-emerald-400" /> Payment Volume</span>
                    <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded bg-blue-400" /> Risk Vector</span>
                    <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded bg-purple-400" /> Policy Bound</span>
                  </div>
                  <span>Peak Anomaly Score: 96/100</span>
                </div>
              </div>
            </AGCard>
          </div>

          {/* RIGHT 1 COL: AI RISK INSIGHTS */}
          <div className="space-y-4">
            <AGCard className="space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] font-mono text-xs">
                <span className="font-bold text-slate-100 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-blue-400" /> AI RISK INSIGHTS
                </span>
                <AGBadge status="LIVE" label="3 INSIGHTS" />
              </div>

              <div className="space-y-3 font-mono text-xs">
                {/* HIGH RISK */}
                <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <AGBadge status="HIGH_RISK" label="HIGH RISK" />
                    <span className="text-red-400 font-bold text-xs">+35 Contribution</span>
                  </div>
                  <p className="font-bold text-slate-200 text-xs">Synthetic identity velocity anomaly detected</p>
                  <p className="text-[10px] text-slate-400 leading-relaxed">
                    SSN issuance timeline conflicts with credit bureau history across 3 recent procurement requests.
                  </p>
                </div>

                {/* MEDIUM RISK */}
                <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <AGBadge status="REVIEW" label="MEDIUM RISK" />
                    <span className="text-amber-400 font-bold text-xs">+28 Contribution</span>
                  </div>
                  <p className="font-bold text-slate-200 text-xs">Device fingerprint collision</p>
                  <p className="text-[10px] text-slate-400 leading-relaxed">
                    WebGL canvas hash matched 14 previously flagged suspicious hardware purchasing sessions.
                  </p>
                </div>

                {/* LOW RISK */}
                <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <AGBadge status="POLICY_SECURE" label="LOW RISK" />
                    <span className="text-emerald-400 font-bold text-xs">-12 Credit</span>
                  </div>
                  <p className="font-bold text-slate-200 text-xs">Verified corporate domain</p>
                  <p className="text-[10px] text-slate-400 leading-relaxed">
                    Pre-approved travel merchant category code and authenticated mTLS agent token.
                  </p>
                </div>
              </div>
            </AGCard>
          </div>

        </div>

        {/* LIVE FRAUD QUEUE TABLE SECTION */}
        <AGCard className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-white/[0.08] font-mono text-xs">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-emerald-400" />
              <span className="font-bold text-slate-100 text-sm">LIVE FRAUD QUEUE</span>
              <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px]">
                {filteredQueue.length} Cases
              </span>
            </div>

            {/* Filter Bar Controls */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter by agent, case, merchant..."
                  className="pl-9 pr-3 py-1.5 bg-slate-950 border border-white/10 rounded-xl text-[11px] text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500/50"
                />
              </div>

              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="bg-slate-950 border border-white/10 rounded-xl px-3 py-1.5 text-[11px] text-slate-300 focus:outline-none"
              >
                <option value="ALL">Risk: All Bands</option>
                <option value="CRITICAL">CRITICAL</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
              </select>

              <select
                value={decisionFilter}
                onChange={(e) => setDecisionFilter(e.target.value)}
                className="bg-slate-950 border border-white/10 rounded-xl px-3 py-1.5 text-[11px] text-slate-300 focus:outline-none"
              >
                <option value="ALL">Decision: All</option>
                <option value="PENDING REVIEW">PENDING REVIEW</option>
                <option value="AUTHORIZED">AUTHORIZED</option>
                <option value="BLOCKED">BLOCKED</option>
              </select>
            </div>
          </div>

          {/* Table Element */}
          <div className="overflow-x-auto font-mono text-xs">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] bg-slate-950/60 text-slate-400 text-[10px] uppercase tracking-wider">
                  <th className="p-3.5">Risk Score</th>
                  <th className="p-3.5">Case ID</th>
                  <th className="p-3.5">Agent Persona</th>
                  <th className="p-3.5">Amount</th>
                  <th className="p-3.5">Merchant</th>
                  <th className="p-3.5">Top Signal</th>
                  <th className="p-3.5">Timestamp</th>
                  <th className="p-3.5">Decision</th>
                  <th className="p-3.5">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filteredQueue.map((c) => {
                  const isSelected = selectedCaseId === c.id;
                  return (
                    <tr
                      key={c.id}
                      onClick={() => setSelectedCaseId(c.id)}
                      className={`cursor-pointer transition-colors ${
                        isSelected ? 'bg-emerald-500/10 border-l-2 border-l-emerald-400' : 'hover:bg-slate-800/40'
                      }`}
                    >
                      <td className="p-3.5">
                        <AGBadge
                          status={
                            c.riskBand === 'CRITICAL'
                              ? 'CRITICAL'
                              : c.riskBand === 'HIGH'
                              ? 'HIGH_RISK'
                              : c.riskBand === 'MEDIUM'
                              ? 'REVIEW'
                              : 'POLICY_SECURE'
                          }
                          label={`${c.riskScore} / 100 (${c.riskBand})`}
                        />
                      </td>

                      <td className="p-3.5 font-bold text-slate-100">{c.id}</td>
                      <td className="p-3.5 text-slate-300">
                        {c.agentName} <span className="text-slate-500 text-[10px]">({c.agentId})</span>
                      </td>
                      <td className="p-3.5 text-emerald-400 font-bold">{c.amount}</td>
                      <td className="p-3.5 text-slate-300">{c.merchant}</td>
                      <td className="p-3.5 text-blue-400 font-semibold">{c.topSignal}</td>
                      <td className="p-3.5 text-slate-400 text-[10px]">{c.timestamp}</td>

                      <td className="p-3.5">
                        <AGBadge
                          status={
                            c.decision === 'BLOCKED'
                              ? 'BLOCKED'
                              : c.decision === 'PENDING REVIEW'
                              ? 'PENDING'
                              : 'APPROVED'
                          }
                        />
                      </td>

                      <td className="p-3.5">
                        <AGButton variant="ghost" size="sm">
                          Inspect
                        </AGButton>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </AGCard>

        {/* CASE INVESTIGATION AGDRAWER (RIGHT-SIDE INSPECTOR DRAWER) */}
        <AGDrawer
          isOpen={!!selectedCase}
          onClose={() => setSelectedCaseId(null)}
          title={selectedCase ? `CASE INVESTIGATION: ${selectedCase.id}` : 'CASE INVESTIGATION'}
          subtitle="AI RISK & SHAP EXPLAINABILITY INSPECTOR"
          footer={
            selectedCase && (
              <div className="space-y-3 font-mono">
                <div className="grid grid-cols-3 gap-2">
                  <AGButton
                    variant="success"
                    size="md"
                    onClick={() => handleUpdateVerdict(selectedCase.id, 'AUTHORIZED')}
                  >
                    AUTHORIZE
                  </AGButton>

                  <AGButton
                    variant="warning"
                    size="md"
                    onClick={() => handleUpdateVerdict(selectedCase.id, 'PENDING REVIEW')}
                  >
                    REVIEW
                  </AGButton>

                  <AGButton
                    variant="danger"
                    size="md"
                    onClick={() => handleUpdateVerdict(selectedCase.id, 'BLOCKED')}
                  >
                    BLOCK
                  </AGButton>
                </div>

                <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-white/[0.08]">
                  <span>Policy Rule: {selectedCase.policyMatched}</span>
                  <span>Ledger Status: Immutably Logged</span>
                </div>
              </div>
            )
          }
        >
          {selectedCase && (
            <div className="space-y-6 font-mono text-xs">
              
              {/* STATUS BANNER */}
              <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-400 block">CURRENT VERDICT</span>
                  <span className="text-base font-bold text-slate-100">{selectedCase.decision}</span>
                </div>

                <AGBadge
                  status={
                    selectedCase.riskBand === 'CRITICAL'
                      ? 'CRITICAL'
                      : selectedCase.riskBand === 'HIGH'
                      ? 'HIGH_RISK'
                      : selectedCase.riskBand === 'MEDIUM'
                      ? 'REVIEW'
                      : 'POLICY_SECURE'
                  }
                  label={`RISK SCORE: ${selectedCase.riskScore} / 100`}
                />
              </div>

              {/* TRANSACTION & AGENT IDENTITY */}
              <div className="space-y-2">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                  TRANSACTION & AGENT IDENTITY
                </h4>
                <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.06] space-y-2 text-[11px]">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Agent Persona:</span>
                    <span className="text-emerald-400 font-bold">{selectedCase.agentName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Agent ID:</span>
                    <span className="text-slate-300">{selectedCase.agentId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Transaction ID:</span>
                    <span className="text-slate-200 font-bold">{selectedCase.transactionId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Amount & Merchant:</span>
                    <span className="text-slate-100 font-bold">{selectedCase.amount} @ {selectedCase.merchant}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Category:</span>
                    <span className="text-slate-300">{selectedCase.category}</span>
                  </div>
                </div>
              </div>

              {/* SIGNAL BREAKDOWN BY CATEGORY */}
              <div className="space-y-2">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                  SIGNAL BREAKDOWN BY CATEGORY
                </h4>
                <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.06] grid grid-cols-2 gap-2 text-[11px]">
                  <div className="flex justify-between p-2 rounded bg-slate-900">
                    <span className="text-slate-400">Identity:</span>
                    <span className="text-blue-400 font-bold">+{selectedCase.categoryContributions.identity}</span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-slate-900">
                    <span className="text-slate-400">Velocity:</span>
                    <span className="text-amber-400 font-bold">+{selectedCase.categoryContributions.velocity}</span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-slate-900">
                    <span className="text-slate-400">Behavioral:</span>
                    <span className="text-purple-400 font-bold">+{selectedCase.categoryContributions.behavioral}</span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-slate-900">
                    <span className="text-slate-400">Financial:</span>
                    <span className="text-red-400 font-bold">+{selectedCase.categoryContributions.financial}</span>
                  </div>
                </div>
              </div>

              {/* DEVICE & NETWORK TELEMETRY */}
              <div className="space-y-2">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                  DEVICE / NETWORK TELEMETRY
                </h4>
                <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1.5 text-[11px]">
                  <div className="flex justify-between">
                    <span className="text-slate-400">IP Node:</span>
                    <span className="text-slate-200">{selectedCase.ipAddress}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Device Fingerprint:</span>
                    <span className="text-slate-300">{selectedCase.deviceFingerprint}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Geo Location:</span>
                    <span className="text-slate-300">{selectedCase.geoLocation}</span>
                  </div>
                </div>
              </div>

              {/* AGENTGUARD POLICY ENFORCEMENT */}
              <div className="space-y-2">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                  AGENTGUARD POLICY ENFORCEMENT
                </h4>
                <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1.5 text-[11px]">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Policy Matched:</span>
                    <span className="text-blue-400 font-bold">{selectedCase.policyMatched}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Execution Result:</span>
                    <span className="text-emerald-400 font-bold">{selectedCase.policyResult}</span>
                  </div>
                </div>
              </div>

              {/* SHAP / EXPLAINABILITY HORIZONTAL BARS */}
              <div className="space-y-3">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                  WHY THIS TRANSACTION WAS FLAGGED (SHAP VECTORS)
                </h4>

                <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.06] space-y-3">
                  {selectedCase.explainability.map((item, idx) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-200">{item.name}</span>
                        <span
                          className={`font-bold ${
                            item.score > 0 ? 'text-red-400' : 'text-emerald-400'
                          }`}
                        >
                          {item.score > 0 ? `+${item.score}` : `${item.score}`}
                        </span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            item.score > 0 ? 'bg-red-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${Math.min(Math.abs(item.score) * 2.5, 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}

                  <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between">
                    <span className="font-bold text-slate-300">FINAL RISK SCORE</span>
                    <span className="font-display font-bold text-lg text-amber-400">
                      {selectedCase.riskScore} / 100 ({selectedCase.riskBand})
                    </span>
                  </div>
                </div>
              </div>

              {/* AI INVESTIGATION BRIEF */}
              <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-2">
                <div className="flex items-center gap-2 text-blue-400 font-bold text-xs">
                  <Brain className="w-4 h-4" />
                  <span>FRAUDGUARD AI ANALYSIS</span>
                </div>
                <p className="text-[11px] text-slate-300 leading-relaxed">{selectedCase.aiBrief}</p>
              </div>

              {/* INVESTIGATION NOTES */}
              <div className="space-y-3">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                  INVESTIGATION NOTES
                </h4>
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newNoteText}
                      onChange={(e) => setNewNoteText(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleAddNote()}
                      placeholder="Add investigation note..."
                      className="flex-1 px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500/50"
                    />
                    <AGButton variant="primary" size="sm" icon={Send} onClick={handleAddNote}>
                      Note
                    </AGButton>
                  </div>

                  {selectedCase.notes.map((n, i) => (
                    <div key={i} className="p-3 rounded-xl bg-slate-950 border border-white/[0.04] space-y-1 text-[11px]">
                      <div className="flex justify-between text-slate-400 text-[10px]">
                        <span className="font-bold text-emerald-400">{n.author}</span>
                        <span>{n.time}</span>
                      </div>
                      <p className="text-slate-200">{n.text}</p>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}
        </AGDrawer>

      </div>
    </AgentPayShell>
  );
}
