'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Plug, RefreshCw } from 'lucide-react';
import { PartnerIntegrationsTabType } from '@/components/partner-integrations/partner-integration-types';
import { MOCK_PARTNER_INTEGRATIONS } from '@/components/partner-integrations/partner-integration-data';

export default function PartnerIntegrationsPage() {
  const [activeTab, setActiveTab] = useState<PartnerIntegrationsTabType>('CONNECTORS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_PARTNER_INTEGRATIONS.filter(i => 
      !search || i.integrationId.toLowerCase().includes(search.toLowerCase()) || i.partnerName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="partner-integrations">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="THIRD-PARTY PSP & PARTNER CONNECTOR CONTROL PLANE"
          title="PARTNER"
          highlightTitle="INTEGRATIONS"
          description="Autonomous PSP integration connectors, encrypted API credential vaults, sandbox testing suites, and real-time health telemetry."
          icon={Plug}
          statusBadge="● CONNECTOR MATRIX LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ACTIVE CONNECTORS" value={`${MOCK_PARTNER_INTEGRATIONS.length}`} subtext="PROCESSED CONNECTORS" accentColor="text-blue-400" />
          <AGMetricCard label="HEALTH SLA" value="100% HEALTHY" subtext="ZERO CONNECTOR DOWN" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG API LATENCY" value="40ms" subtext="SUB-50MS API RESPONSE" accentColor="text-emerald-400" />
          <AGMetricCard label="CREDENTIAL VAULT" value="ENCRYPTED" subtext="AES-256 SECURED" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Integration ID, Partner Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['CONNECTORS', 'CREDENTIAL_VAULT', 'SANDBOX_TESTING', 'HEALTH_TELEMETRY', 'AUDIT'] as PartnerIntegrationsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'CONNECTORS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">INTEGRATION ID</th>
                  <th className="p-3">PARTNER NAME</th>
                  <th className="p-3">CONNECTOR TYPE</th>
                  <th className="p-3">ENVIRONMENT</th>
                  <th className="p-3">API LATENCY</th>
                  <th className="p-3">HEALTH STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(i => (
                  <tr key={i.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{i.integrationId}</td>
                    <td className="p-3 font-bold text-slate-200">{i.partnerName}</td>
                    <td className="p-3 font-bold text-purple-400">{i.connectorType}</td>
                    <td className="p-3 text-emerald-400 font-mono font-bold">{i.environment}</td>
                    <td className="p-3 text-emerald-400 font-mono">{i.apiLatencyMs} ms</td>
                    <td className="p-3"><AGBadge status={i.healthStatus} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'CONNECTORS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
