'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { FraudAnomalySignalsTabType } from '@/components/fraud-anomaly-signals/fraud-anomaly-signal-types';
import { MOCK_FRAUD_ANOMALY_SIGNALS } from '@/components/fraud-anomaly-signals/fraud-anomaly-signal-data';

export default function FraudAnomalySignalsPage() {
  const [activeTab, setActiveTab] = useState<FraudAnomalySignalsTabType>('ANOMALY_SIGNALS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_FRAUD_ANOMALY_SIGNALS.filter(s => 
      !search || s.signalId.toLowerCase().includes(search.toLowerCase()) || s.transactionRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="fraud-anomaly-signals">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="REAL-TIME NEURAL FRAUD ANOMALY & RISK SIGNAL DETECTOR PLANE"
          title="FRAUD ANOMALY"
          highlightTitle="SIGNALS"
          description="Real-time neural risk scoring, velocity anomaly detection, behavioral trajectory shift analysis, and automatic fraud mitigation."
          icon={AlertTriangle}
          statusBadge="● FRAUD NEURAL DETECTOR LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ANOMALY SIGNALS" value={`${MOCK_FRAUD_ANOMALY_SIGNALS.length}`} subtext="PROCESSED SIGNALS" accentColor="text-blue-400" />
          <AGMetricCard label="AVG ANOMALY SCORE" value="15 / 100" subtext="LOW RISK ENVIRONMENT" accentColor="text-emerald-400" />
          <AGMetricCard label="NEURAL LATENCY" value="< 12ms" subtext="REAL-TIME EVALUATION" accentColor="text-emerald-400" />
          <AGMetricCard label="PRECISION RATE" value="99.98%" subtext="ZERO FALSE POSITIVES" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Signal ID, Transaction Ref..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['ANOMALY_SIGNALS', 'NEURAL_SCORES', 'GEOGRAPHIC_SPIKES', 'AUDIT'] as FraudAnomalySignalsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'ANOMALY_SIGNALS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SIGNAL ID</th>
                  <th className="p-3">TRANSACTION REF</th>
                  <th className="p-3">ANOMALY SCORE</th>
                  <th className="p-3">SIGNAL CATEGORY</th>
                  <th className="p-3">RECOMMENDED ACTION</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.signalId}</td>
                    <td className="p-3 font-bold text-purple-400">{s.transactionRef}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.anomalyScore}</td>
                    <td className="p-3 text-slate-200 font-mono">{s.signalCategory}</td>
                    <td className="p-3 text-emerald-400 font-bold">{s.recommendedAction}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'ANOMALY_SIGNALS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
