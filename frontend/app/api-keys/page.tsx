'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Key, RefreshCw } from 'lucide-react';
import { ApiKeysTabType } from '@/components/api-keys/api-key-types';
import { MOCK_API_KEYS } from '@/components/api-keys/api-key-data';

export default function ApiKeysPage() {
  const [activeTab, setActiveTab] = useState<ApiKeysTabType>('KEYS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_API_KEYS.filter(a => 
      !search || a.keyId.toLowerCase().includes(search.toLowerCase()) || a.name.toLowerCase().includes(search.toLowerCase()) || a.prefix.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="api-keys">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="API KEY MANAGEMENT & SCOPED PERMISSIONS PLANE"
          title="API KEY"
          highlightTitle="MANAGEMENT"
          description="Granular API key creation, RBAC permission scoping, IP CIDR restriction whitelisting, key rotation cadence, and instant revocation."
          icon={Key}
          statusBadge="● KEY VAULT SECURE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ACTIVE API KEYS" value={`${MOCK_API_KEYS.length}`} subtext="PROVISIONED KEYS" accentColor="text-blue-400" />
          <AGMetricCard label="SECURITY RATING" value="100% ENCRYPTED" subtext="AES-256 VAULT STORED" accentColor="text-emerald-400" />
          <AGMetricCard label="IP WHITELISTING" value="STRICT CIDR" subtext="ZERO UNTRUSTED ACCESS" accentColor="text-emerald-400" />
          <AGMetricCard label="KEY ROTATION SLA" value="90 DAYS" subtext="AUTOMATED EXPIRY WARN" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Key ID, Name, Prefix..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['KEYS', 'SCOPES', 'IP_WHITELIST', 'KEY_ROTATION', 'AUDIT'] as ApiKeysTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'KEYS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">KEY ID</th>
                  <th className="p-3">NAME</th>
                  <th className="p-3">KEY PREFIX</th>
                  <th className="p-3">PERMITTED SCOPES</th>
                  <th className="p-3">LAST USED</th>
                  <th className="p-3">IP RESTRICTION</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(a => (
                  <tr key={a.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{a.keyId}</td>
                    <td className="p-3 font-bold text-slate-200">{a.name}</td>
                    <td className="p-3 text-purple-400 font-mono font-bold">{a.prefix}</td>
                    <td className="p-3 text-slate-300 font-mono">{a.scopes}</td>
                    <td className="p-3 text-slate-400">{a.lastUsed}</td>
                    <td className="p-3 text-amber-400 font-mono">{a.ipRestriction}</td>
                    <td className="p-3"><AGBadge status={a.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'KEYS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
