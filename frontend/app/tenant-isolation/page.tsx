'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Layers, RefreshCw } from 'lucide-react';
import { TenantIsolationTabType } from '@/components/tenant-isolation/tenant-isolation-types';
import { MOCK_TENANT_ISOLATIONS } from '@/components/tenant-isolation/tenant-isolation-data';

export default function TenantIsolationPage() {
  const [activeTab, setActiveTab] = useState<TenantIsolationTabType>('TENANTS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_TENANT_ISOLATIONS.filter(t => 
      !search || t.tenantId.toLowerCase().includes(search.toLowerCase()) || t.organizationName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="tenant-isolation">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="MULTI-TENANT ISOLATION & VIRTUAL PLATFORM ARCHITECTURE PLANE"
          title="MULTI-TENANT"
          highlightTitle="ISOLATION"
          description="Row-level database tenant isolation, virtual private ledger partitioning, multi-org RBAC policies, and SOC2 isolation SLA."
          icon={Layers}
          statusBadge="● TENANT ISOLATION BOUNDARY SECURE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ISOLATED TENANTS" value={`${MOCK_TENANT_ISOLATIONS.length}`} subtext="PROVISIONED ORGANIZATIONS" accentColor="text-blue-400" />
          <AGMetricCard label="ISOLATION SLA" value="100% STRICT" subtext="ZERO CROSS-TENANT LEAK" accentColor="text-emerald-400" />
          <AGMetricCard label="DB PARTITIONING" value="ROW-LEVEL ENCRYPT" subtext="AES-256 PER TENANT" accentColor="text-emerald-400" />
          <AGMetricCard label="COMPLIANCE" value="SOC2 TYPE II" subtext="VIRTUAL PRIVATE LEDGER" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Tenant ID, Organization..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['TENANTS', 'ROW_LEVEL_ISOLATION', 'VIRTUAL_PLATFORMS', 'RBAC_POLICIES', 'AUDIT'] as TenantIsolationTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'TENANTS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">TENANT ID</th>
                  <th className="p-3">ORGANIZATION NAME</th>
                  <th className="p-3">ISOLATION TIER</th>
                  <th className="p-3">ALLOCATED QUOTA</th>
                  <th className="p-3">COMPLIANCE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(t => (
                  <tr key={t.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{t.tenantId}</td>
                    <td className="p-3 font-bold text-slate-200">{t.organizationName}</td>
                    <td className="p-3 font-bold text-purple-400">{t.isolationTier}</td>
                    <td className="p-3 text-slate-300 font-mono">{t.allocatedQuota}</td>
                    <td className="p-3 text-emerald-400 font-bold">{t.complianceLevel}</td>
                    <td className="p-3"><AGBadge status={t.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'TENANTS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
