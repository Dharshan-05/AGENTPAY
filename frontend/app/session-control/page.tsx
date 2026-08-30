'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { KeyRound, RefreshCw } from 'lucide-react';
import { SessionControlTabType } from '@/components/session-control/session-control-types';
import { MOCK_SESSION_CONTROL } from '@/components/session-control/session-control-data';

export default function SessionControlPage() {
  const [activeTab, setActiveTab] = useState<SessionControlTabType>('SESSIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SESSION_CONTROL.filter(s => 
      !search || s.sessionId.toLowerCase().includes(search.toLowerCase()) || s.agentRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="session-control">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="CHECKOUT SESSION SECURITY & AUTHENTICATION PLANE"
          title="SESSION"
          highlightTitle="CONTROL"
          description="Autonomous agent checkout session management, mTLS/JWT authentication telemetry, TTL session expiry, and FraudGuard signals."
          icon={KeyRound}
          statusBadge="● SESSIONS VAULT ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ACTIVE SESSIONS" value={`${MOCK_SESSION_CONTROL.length}`} subtext="ENCRYPTED SESSIONS" accentColor="text-blue-400" />
          <AGMetricCard label="mTLS AUTH RATE" value="100% mTLS" subtext="HARDWARE SECURITY MODULE" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG SESSION RISK" value="7 / 100" subtext="NEURAL FRAUDGUARD RISK" accentColor="text-emerald-400" />
          <AGMetricCard label="SECURITY STATUS" value="ZERO LEAKS" subtext="MASKED ATTRIBUTES" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Session ID, Agent..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['SESSIONS', 'AUTHENTICATION', 'IP_GEOLOCATION', 'FRAUDGUARD_SIGNALS', 'EXPIRED', 'AUDIT'] as SessionControlTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'SESSIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SESSION ID</th>
                  <th className="p-3">AGENT REF</th>
                  <th className="p-3">IP ADDRESS (MASKED)</th>
                  <th className="p-3">AUTH METHOD</th>
                  <th className="p-3">RISK SCORE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.sessionId}</td>
                    <td className="p-3 font-bold text-purple-400">{s.agentRef}</td>
                    <td className="p-3 font-mono text-slate-400">{s.ipAddressMasked}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.authMethod}</td>
                    <td className="p-3 text-emerald-400 font-bold">{s.riskScore} / 100</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'SESSIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
