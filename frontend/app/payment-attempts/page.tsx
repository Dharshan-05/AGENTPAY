'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Zap, RefreshCw } from 'lucide-react';
import { AttemptsTabType } from '@/components/payment-attempts/payment-attempt-types';
import { MOCK_ATTEMPTS } from '@/components/payment-attempts/payment-attempt-data';

export default function PaymentAttemptsPage() {
  const [activeTab, setActiveTab] = useState<AttemptsTabType>('TELEMETRY');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_ATTEMPTS.filter(a => 
      !search || a.attemptId.toLowerCase().includes(search.toLowerCase()) || a.paymentIntentId.toLowerCase().includes(search.toLowerCase()) || a.processor.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="payment-attempts">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="PAYMENT ATTEMPT & CONNECTOR RETRY TELEMETRY PLANE"
          title="PAYMENT"
          highlightTitle="ATTEMPTS"
          description="Multi-processor retry attempt tracking, 3DS authentication telemetry, HTTP response code audit, and processor latency telemetry."
          icon={Zap}
          statusBadge="● ATTEMPT TELEMETRY LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="PAYMENT ATTEMPTS" value={`${MOCK_ATTEMPTS.length}`} subtext="PROCESSED ATTEMPTS" accentColor="text-blue-400" />
          <AGMetricCard label="FIRST-ATTEMPT AUTH" value="99.2%" subtext="SUB-150MS LATENCY" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG PROCESSOR SPEED" value="130ms" subtext="PSP RESPONSE LATENCY" accentColor="text-emerald-400" />
          <AGMetricCard label="RETRY SUCCESS RATE" value="100%" subtext="FAILOVER ROUTING MATCH" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Attempt ID, PI ID, Processor..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['TELEMETRY', 'AUTHORIZED', 'CAPTURED', 'FAILED_RETRIES', 'RESPONSE_CODES', 'CONNECTOR_SPLIT', 'AUDIT'] as AttemptsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'TELEMETRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">ATTEMPT ID</th>
                  <th className="p-3">PI ID</th>
                  <th className="p-3">ORDER ID</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3">ATTEMPT #</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">LATENCY</th>
                  <th className="p-3">RESPONSE CODE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(a => (
                  <tr key={a.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{a.attemptId}</td>
                    <td className="p-3 font-bold text-purple-400">{a.paymentIntentId}</td>
                    <td className="p-3 text-slate-300">{a.orderId}</td>
                    <td className="p-3 font-bold text-slate-200">{a.processor}</td>
                    <td className="p-3 text-slate-300">Attempt #{a.attemptNumber}</td>
                    <td className="p-3 font-bold text-emerald-400">{a.amount}</td>
                    <td className="p-3 text-emerald-400 font-bold">{a.latencyMs}ms</td>
                    <td className="p-3 text-slate-400 font-mono text-[10px]">{a.responseCode}</td>
                    <td className="p-3"><AGBadge status={a.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'TELEMETRY' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
