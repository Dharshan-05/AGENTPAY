'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Building2, RefreshCw } from 'lucide-react';
import { SupplierPayoutsTabType } from '@/components/supplier-payouts/supplier-payout-types';
import { MOCK_SUPPLIER_PAYOUTS } from '@/components/supplier-payouts/supplier-payout-data';

export default function SupplierPayoutsPage() {
  const [activeTab, setActiveTab] = useState<SupplierPayoutsTabType>('PAYOUTS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SUPPLIER_PAYOUTS.filter(s => 
      !search || s.payoutId.toLowerCase().includes(search.toLowerCase()) || s.vendorName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="supplier-payouts">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="VENDOR & MARKETPLACE SPLIT PAYOUT PLANE"
          title="SUPPLIER"
          highlightTitle="PAYOUTS"
          description="Automated vendor revenue splits, marketplace payout scheduling, batch transfer settlement, and holding rules."
          icon={Building2}
          statusBadge="● SUPPLIER PAYOUT ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="SUPPLIER PAYOUTS" value={`${MOCK_SUPPLIER_PAYOUTS.length}`} subtext="ACTIVE VENDOR BATCHES" accentColor="text-blue-400" />
          <AGMetricCard label="SETTLED PAYOUTS" value="$127.5K" subtext="TOTAL VENDOR TRANSFERS" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG SPLIT RATE" value="82.5%" subtext="VENDOR REVENUE SHARE" accentColor="text-emerald-400" />
          <AGMetricCard label="HELD FUNDS" value="$0.00" subtext="ZERO RESERVE STOPS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Payout ID, Vendor..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['PAYOUTS', 'VENDORS', 'SPLIT_RULES', 'BATCHES', 'SETTLED', 'HELD', 'AUDIT'] as SupplierPayoutsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'PAYOUTS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">PAYOUT ID</th>
                  <th className="p-3">VENDOR NAME</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">CURRENCY</th>
                  <th className="p-3">SPLIT %</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.payoutId}</td>
                    <td className="p-3 font-bold text-slate-200">{s.vendorName}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.amount}</td>
                    <td className="p-3 text-slate-300">{s.currency}</td>
                    <td className="p-3 text-purple-400 font-bold">{s.splitPercentage}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'PAYOUTS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
