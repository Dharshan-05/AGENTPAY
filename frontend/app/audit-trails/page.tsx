'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { FileCode, RefreshCw } from 'lucide-react';
import { AuditTrailsTabType } from '@/components/audit-trails/audit-trail-types';
import { MOCK_AUDIT_TRAILS } from '@/components/audit-trails/audit-trail-data';

export default function AuditTrailsPage() {
  const [activeTab, setActiveTab] = useState<AuditTrailsTabType>('EVENT_LOGS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_AUDIT_TRAILS.filter(a => 
      !search || a.auditId.toLowerCase().includes(search.toLowerCase()) || a.actor.toLowerCase().includes(search.toLowerCase()) || a.action.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="audit-trails">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="IMMUTABLE AUDIT TRAIL & CRYPTOGRAPHIC HASH CHAIN PLANE"
          title="IMMUTABLE"
          highlightTitle="AUDIT TRAILS"
          description="Cryptographically chained event audit trails, tamper-evident hash verification, actor authorization logs, and SOC2/PCI compliance."
          icon={FileCode}
          statusBadge="● HASH CHAIN VERIFIED"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="AUDIT ENTRIES" value={`${MOCK_AUDIT_TRAILS.length}`} subtext="CHAINED LOG ENTRIES" accentColor="text-blue-400" />
          <AGMetricCard label="CHAIN INTEGRITY" value="100% VERIFIED" subtext="ZERO HASH TAMPERING" accentColor="text-emerald-400" />
          <AGMetricCard label="CRYPTO ALGORITHM" value="SHA-256" subtext="MERKLE TREE VERIFIED" accentColor="text-emerald-400" />
          <AGMetricCard label="COMPLIANCE READY" value="SOC2 / PCI SAQ-A" subtext="AUDIT EXPORT READY" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Audit ID, Actor, Action..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['EVENT_LOGS', 'HASH_CHAINS', 'SECURITY_ACTORS', 'TAMPER_CHECK', 'EXPORT'] as AuditTrailsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'EVENT_LOGS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">AUDIT ID</th>
                  <th className="p-3">TIMESTAMP</th>
                  <th className="p-3">ACTOR</th>
                  <th className="p-3">ACTION</th>
                  <th className="p-3">ENTITY TYPE</th>
                  <th className="p-3">HASH PREVIEW</th>
                  <th className="p-3">VERIFICATION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(a => (
                  <tr key={a.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{a.auditId}</td>
                    <td className="p-3 text-slate-400">{a.timestamp}</td>
                    <td className="p-3 font-bold text-purple-400">{a.actor}</td>
                    <td className="p-3 text-slate-200">{a.action}</td>
                    <td className="p-3 text-slate-300 font-mono">{a.entityType}</td>
                    <td className="p-3 text-slate-400 font-mono">{a.hashPreview}</td>
                    <td className="p-3 text-emerald-400 font-bold">{a.verificationStatus}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'EVENT_LOGS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
