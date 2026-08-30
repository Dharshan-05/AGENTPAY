'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Lock, RefreshCw } from 'lucide-react';
import { VaultTokenMigrationTabType } from '@/components/vault-token-migration/vault-token-migration-types';
import { MOCK_VAULT_TOKEN_MIGRATIONS } from '@/components/vault-token-migration/vault-token-migration-data';

export default function VaultTokenMigrationPage() {
  const [activeTab, setActiveTab] = useState<VaultTokenMigrationTabType>('MIGRATION_JOBS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_VAULT_TOKEN_MIGRATIONS.filter(v => 
      !search || v.migrationId.toLowerCase().includes(search.toLowerCase()) || v.sourceVault.toLowerCase().includes(search.toLowerCase()) || v.targetVault.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="vault-token-migration">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="CROSS-VAULT TOKEN MIGRATION & PCI PORTABILITY PLANE"
          title="TOKEN VAULT"
          highlightTitle="MIGRATION"
          description="PCI SAQ-A token vault migration, cross-PSP credential portability, Hardware Security Module re-keying, and zero-downtime token mapping."
          icon={Lock}
          statusBadge="● TOKEN PORTABILITY ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TOTAL MIGRATED TOKENS" value="73,600 Tokens" subtext="100% PORTED SECURELY" accentColor="text-blue-400" />
          <AGMetricCard label="PORTABILITY SUCCESS" value="100% SUCCESS" subtext="ZERO LOST CREDENTIALS" accentColor="text-emerald-400" />
          <AGMetricCard label="ENCRYPTION" value="AES-256-GCM" subtext="HSM RE-KEYED" accentColor="text-emerald-400" />
          <AGMetricCard label="COMPLIANCE" value="PCI SAQ-A" subtext="AUDIT TRAIL SECURED" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Migration ID, Vault..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['MIGRATION_JOBS', 'PORTABILITY_EXPORTS', 'KEY_RE_ENCRYPTION', 'AUDIT'] as VaultTokenMigrationTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'MIGRATION_JOBS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">MIGRATION ID</th>
                  <th className="p-3">SOURCE VAULT</th>
                  <th className="p-3">TARGET VAULT</th>
                  <th className="p-3">TOKENS MIGRATED</th>
                  <th className="p-3">ENCRYPTION</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(v => (
                  <tr key={v.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{v.migrationId}</td>
                    <td className="p-3 font-bold text-purple-400 font-mono">{v.sourceVault}</td>
                    <td className="p-3 font-bold text-emerald-400 font-mono">{v.targetVault}</td>
                    <td className="p-3 text-slate-200 font-bold">{v.totalTokensMigrated.toLocaleString()} tokens</td>
                    <td className="p-3 text-amber-400 font-mono">{v.encryptionAlgorithm}</td>
                    <td className="p-3"><AGBadge status={v.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'MIGRATION_JOBS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
