'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Coins, RefreshCw, Plus } from 'lucide-react';
import { StoreCreditTabType } from '@/components/store-credit/store-credit-types';
import { MOCK_STORE_CREDIT } from '@/components/store-credit/store-credit-data';

export default function StoreCreditPage() {
  const [activeTab, setActiveTab] = useState<StoreCreditTabType>('BALANCES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_STORE_CREDIT.filter(s => 
      !search || s.creditId.toLowerCase().includes(search.toLowerCase()) || s.customer.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="store-credit">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="CUSTOMER STORE CREDIT & ACCOUNT BALANCE PLANE"
          title="STORE"
          highlightTitle="CREDIT"
          description="Customer store credit balance ledger, refund credit issuance, automated checkout balance application, and audit trace."
          icon={Coins}
          statusBadge="● CREDIT LEDGER ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Add Credit Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> ISSUE CREDIT</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="CREDIT ACCOUNTS" value={`${MOCK_STORE_CREDIT.length}`} subtext="ACTIVE BALANCES" accentColor="text-blue-400" />
          <AGMetricCard label="TOTAL OUTSTANDING" value="$5,450.00" subtext="STORE CREDIT LIABILITIES" accentColor="text-emerald-400" />
          <AGMetricCard label="AUTO-APPLY RATE" value="100%" subtext="AUTOMATED CHECKOUT BIND" accentColor="text-emerald-400" />
          <AGMetricCard label="ZERO VARIANCE" value="VERIFIED" subtext="DOUBLE-ENTRY MATCH" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Credit ID, Customer..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['BALANCES', 'ADJUSTMENTS', 'AUTO_APPLY', 'EXPIRATIONS', 'LEDGER', 'RECONCILIATION', 'AUDIT'] as StoreCreditTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'BALANCES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">CREDIT ID</th>
                  <th className="p-3">CUSTOMER</th>
                  <th className="p-3">BALANCE</th>
                  <th className="p-3">LAST MOVEMENT</th>
                  <th className="p-3">AUTO-APPLY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.creditId}</td>
                    <td className="p-3 font-bold text-slate-200">{s.customer}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.balance} ({s.currency})</td>
                    <td className="p-3 text-slate-400">{s.lastMovement}</td>
                    <td className="p-3 text-emerald-400 font-bold">{s.autoApply ? 'ENABLED' : 'DISABLED'}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'BALANCES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
