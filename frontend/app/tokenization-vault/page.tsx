'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Lock, RefreshCw } from 'lucide-react';
import { TokenizationVaultTabType } from '@/components/tokenization-vault/tokenization-vault-types';
import { MOCK_TOKENIZATION_VAULT } from '@/components/tokenization-vault/tokenization-vault-data';

export default function TokenizationVaultPage() {
  const [activeTab, setActiveTab] = useState<TokenizationVaultTabType>('VAULT_TOKENS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_TOKENIZATION_VAULT.filter(v => 
      !search || v.tokenId.toLowerCase().includes(search.toLowerCase()) || v.surrogateToken.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="tokenization-vault">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="PCI SAQ-A VAULT & SURROGATE TOKENIZATION CONTROL PLANE"
          title="TOKENIZATION"
          highlightTitle="VAULT CONTROL"
          description="Zero-raw-PAN tokenization vault, Hardware Security Module (HSM) Key Encryption Keys (KEK), and PCI DSS compliance auditing."
          icon={Lock}
          statusBadge="● PCI DSS LEVEL 1 VAULT ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="VAULTED TOKENS" value={`${MOCK_TOKENIZATION_VAULT.length}`} subtext="ACTIVE SURROGATE TOKENS" accentColor="text-blue-400" />
          <AGMetricCard label="PCI COMPLIANCE" value="SAQ-A CERTIFIED" subtext="ZERO RAW CARD DATA" accentColor="text-emerald-400" />
          <AGMetricCard label="ENCRYPTION" value="AES-256-GCM" subtext="HSM HARDWARE KEK" accentColor="text-emerald-400" />
          <AGMetricCard label="TOKEN RESOLUTION" value="< 5ms" subtext="INSTANT VAULT DECRYPT" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Token ID, Surrogate Token..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['VAULT_TOKENS', 'KEY_ROTATION', 'ENCRYPTION_POLICIES', 'PCI_COMPLIANCE', 'AUDIT'] as TokenizationVaultTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'VAULT_TOKENS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">TOKEN ID</th>
                  <th className="p-3">SURROGATE TOKEN</th>
                  <th className="p-3">TOKEN TYPE</th>
                  <th className="p-3">KEY ENCRYPTION KEY</th>
                  <th className="p-3">TOKEN EXPIRY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(v => (
                  <tr key={v.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{v.tokenId}</td>
                    <td className="p-3 font-bold text-purple-400 font-mono">{v.surrogateToken}</td>
                    <td className="p-3 text-slate-200">{v.tokenType}</td>
                    <td className="p-3 text-amber-400 font-mono">{v.keyEncryptionKey}</td>
                    <td className="p-3 text-slate-400">{v.tokenExpiry}</td>
                    <td className="p-3"><AGBadge status={v.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'VAULT_TOKENS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
