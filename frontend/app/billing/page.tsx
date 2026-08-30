'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { CreditCard, RefreshCw } from 'lucide-react';
import { BillingTabType } from '@/components/billing/billing-types';
import { MOCK_BILLING } from '@/components/billing/billing-data';

export default function BillingPage() {
  const [activeTab, setActiveTab] = useState<BillingTabType>('CYCLES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_BILLING.filter(b => 
      !search || b.billingId.toLowerCase().includes(search.toLowerCase()) || b.customer.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="billing">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="USAGE-BASED BILLING & METERING ENGINE"
          title="BILLING"
          highlightTitle="OPERATIONS"
          description="Real-time API metered usage aggregation, automated billing cycle closing, credits & balance tracking, and invoice dispatch."
          icon={CreditCard}
          statusBadge="● BILLING METER ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="BILLING CYCLES" value={`${MOCK_BILLING.length}`} subtext="ACTIVE CYCLES" accentColor="text-blue-400" />
          <AGMetricCard label="METERED UNITS" value="2,310" subtext="API EXECUTIONS" accentColor="text-emerald-400" />
          <AGMetricCard label="METERED REVENUE" value="$2,310.00" subtext="USAGE ACCRUAL" accentColor="text-emerald-400" />
          <AGMetricCard label="CREDIT BALANCE" value="$500.00" subtext="PREPAID CREDITS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Billing ID, Customer..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['CYCLES', 'USAGE', 'CHARGES', 'CREDITS', 'TAXES', 'BALANCES', 'PROFILES', 'AUDIT'] as BillingTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'CYCLES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">BILLING ID</th>
                  <th className="p-3">CUSTOMER</th>
                  <th className="p-3">PERIOD</th>
                  <th className="p-3">METERED UNITS</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(b => (
                  <tr key={b.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{b.billingId}</td>
                    <td className="p-3 text-slate-200">{b.customer}</td>
                    <td className="p-3 text-slate-400">{b.cyclePeriod}</td>
                    <td className="p-3 font-bold text-emerald-400">{b.usageUnits} units</td>
                    <td className="p-3 font-bold text-slate-100">{b.meteredAmount}</td>
                    <td className="p-3"><AGBadge status={b.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'CYCLES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
