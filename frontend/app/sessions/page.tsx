'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { KeyRound, RefreshCw } from 'lucide-react';
import { SessionsTabType } from '@/components/sessions/session-types';
import { MOCK_SESSIONS } from '@/components/sessions/session-data';

export default function SessionsPage() {
  const [activeTab, setActiveTab] = useState<SessionsTabType>('ACTIVE');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SESSIONS.filter(s => 
      !search || s.sessionId.toLowerCase().includes(search.toLowerCase()) || s.customer.toLowerCase().includes(search.toLowerCase()) || s.agentId.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="sessions">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="CHECKOUT SESSION LIFECYCLE & STATE CONTROL PLANE"
          title="CHECKOUT"
          highlightTitle="SESSIONS"
          description="Autonomous agent checkout session management, TTL token expiration, 3DS authentication state, and session recovery."
          icon={KeyRound}
          statusBadge="● SESSION ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="CHECKOUT SESSIONS" value={`${MOCK_SESSIONS.length}`} subtext="ACTIVE SESSIONS" accentColor="text-blue-400" />
          <AGMetricCard label="SESSION CONVERSION" value="99.4%" subtext="COMPLETED CHECKOUTS" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG SESSION TIME" value="1.8m" subtext="FAST AGENT CHECKOUT" accentColor="text-emerald-400" />
          <AGMetricCard label="ABANDONED RATE" value="0.6%" subtext="SUB-1% ABANDONMENT" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Session ID, Customer, Agent..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['ACTIVE', 'OPEN', 'PAYMENT_PENDING', 'AUTHENTICATING', 'COMPLETED', 'EXPIRED', 'AUDIT'] as SessionsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'ACTIVE' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SESSION ID</th>
                  <th className="p-3">CUSTOMER</th>
                  <th className="p-3">MERCHANT</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">SESSION AMOUNT</th>
                  <th className="p-3">TTL EXPIRES</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.sessionId}</td>
                    <td className="p-3 text-slate-200">{s.customer}</td>
                    <td className="p-3 text-slate-300">{s.merchant}</td>
                    <td className="p-3 font-bold text-purple-400">{s.agentId}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.amount}</td>
                    <td className="p-3 text-amber-400 font-bold">{s.ttlExpiresAt}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'ACTIVE' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
