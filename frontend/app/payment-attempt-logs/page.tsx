'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Zap, RefreshCw } from 'lucide-react';
import { PaymentAttemptLogsTabType } from '@/components/payment-attempt-logs/payment-attempt-logs-types';
import { MOCK_PAYMENT_ATTEMPT_LOGS } from '@/components/payment-attempt-logs/payment-attempt-logs-data';

export default function PaymentAttemptLogsPage() {
  const [activeTab, setActiveTab] = useState<PaymentAttemptLogsTabType>('ATTEMPTS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_PAYMENT_ATTEMPT_LOGS.filter(p => 
      !search || p.attemptId.toLowerCase().includes(search.toLowerCase()) || p.paymentIntentRef.toLowerCase().includes(search.toLowerCase()) || p.processor.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="payment-attempt-logs">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="PAYMENT ATTEMPT LOGS & RETRY MATRIX PLANE"
          title="PAYMENT ATTEMPT"
          highlightTitle="LOGS"
          description="Payment attempt execution trace, retry matrix rules, PSP response codes, 3DS authentication telemetry, and latency metrics."
          icon={Zap}
          statusBadge="● ATTEMPT MONITOR ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TOTAL ATTEMPTS" value={`${MOCK_PAYMENT_ATTEMPT_LOGS.length}`} subtext="PROCESSED ATTEMPTS" accentColor="text-blue-400" />
          <AGMetricCard label="FIRST-ATTEMPT SUCCESS" value="100% SUCCESS" subtext="ZERO RETRIES REQUIRED" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG LATENCY" value="197 ms" subtext="SUB-250MS LATENCY SLA" accentColor="text-emerald-400" />
          <AGMetricCard label="PSP RESPONSE CODE" value="200 OK" subtext="ALL ATTEMPTS AUTHORIZED" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Attempt ID, PI Ref, Processor..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['ATTEMPTS', 'RETRY_MATRIX', 'PSP_RESPONSES', 'LATENCY_METRICS', '3DS_VERIFICATIONS', 'AUDIT'] as PaymentAttemptLogsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'ATTEMPTS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">ATTEMPT ID</th>
                  <th className="p-3">PI REF</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3">ATTEMPT NO</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">RESPONSE CODE</th>
                  <th className="p-3">LATENCY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(p => (
                  <tr key={p.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{p.attemptId}</td>
                    <td className="p-3 font-bold text-purple-400">{p.paymentIntentRef}</td>
                    <td className="p-3 text-slate-200">{p.processor}</td>
                    <td className="p-3 text-slate-400">#{p.attemptNumber}</td>
                    <td className="p-3 font-bold text-emerald-400">{p.amount}</td>
                    <td className="p-3 text-emerald-400 font-mono font-bold">{p.responseCode}</td>
                    <td className="p-3 text-slate-300 font-mono">{p.latencyMs} ms</td>
                    <td className="p-3"><AGBadge status={p.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'ATTEMPTS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
