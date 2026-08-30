'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { ShieldAlert, RefreshCw, Lock } from 'lucide-react';
import { AuditLogsTabType } from '@/components/audit-logs/audit-log-types';
import { MOCK_AUDIT_LOGS } from '@/components/audit-logs/audit-log-data';

export default function AuditLogsPage() {
  const [activeTab, setActiveTab] = useState<AuditLogsTabType>('STREAM');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_AUDIT_LOGS.filter(a => 
      !search || a.logId.toLowerCase().includes(search.toLowerCase()) || a.action.toLowerCase().includes(search.toLowerCase()) || a.actor.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="audit-logs">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="CENTRALIZED SECURITY & FINANCIAL AUDIT LOG PLANE"
          title="SECURITY &"
          highlightTitle="AUDIT LOGS"
          description="Cryptographically chained SHA-256 system audit stream, SOC2 compliance logging, actor activity correlation, and tamper detection."
          icon={ShieldAlert}
          statusBadge="● AUDIT CHAIN VERIFIED"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="AUDIT EVENTS 24H" value="184,920" subtext="REAL-TIME LOG STREAM" accentColor="text-blue-400" />
          <AGMetricCard label="CHAIN INTEGRITY" value="100% VERIFIED" subtext="SHA-256 HASH CHAIN" accentColor="text-emerald-400" />
          <AGMetricCard label="TAMPER STOPS" value="00" subtext="ZERO INTEGRITY GAPS" accentColor="text-emerald-400" />
          <AGMetricCard label="RETENTION POLICY" value="7 YEARS" subtext="SOC2 & PCI COMPLIANT" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Log ID, Actor, Action..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['STREAM', 'SECURITY_EVENTS', 'FINANCIAL_POSTINGS', 'POLICY_EVALS', 'CHAIN_INTEGRITY', 'EXPORTS', 'AUDIT'] as AuditLogsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'STREAM' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">LOG ID</th>
                  <th className="p-3">ACTOR</th>
                  <th className="p-3">ACTION</th>
                  <th className="p-3">RESOURCE ID</th>
                  <th className="p-3">IP ADDRESS</th>
                  <th className="p-3">TIMESTAMP</th>
                  <th className="p-3">SHA-256 HASH</th>
                  <th className="p-3">INTEGRITY</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(a => (
                  <tr key={a.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-purple-400">{a.logId}</td>
                    <td className="p-3 font-bold text-blue-400">{a.actor}</td>
                    <td className="p-3 font-bold text-slate-200">{a.action}</td>
                    <td className="p-3 text-slate-300">{a.resourceId}</td>
                    <td className="p-3 text-slate-400">{a.ipAddress}</td>
                    <td className="p-3 text-slate-500">{a.timestamp}</td>
                    <td className="p-3 text-slate-500 font-mono text-[10px]">{a.sha256Hash}</td>
                    <td className="p-3"><AGBadge status={a.integrity} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'STREAM' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
