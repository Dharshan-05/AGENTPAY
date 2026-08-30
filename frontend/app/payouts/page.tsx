'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { ArrowUpRight, RefreshCw, Download, Plus, ArrowRight } from 'lucide-react';
import { PayoutTabType, PayoutRecord } from '@/components/payouts/payout-types';
import { MOCK_PAYOUTS } from '@/components/payouts/payout-data';

export default function PayoutsPage() {
  const [activeTab, setActiveTab] = useState<PayoutTabType>('REGISTRY');
  const [search, setSearch] = useState('');
  const [selectedPo, setSelectedPo] = useState<PayoutRecord | null>(null);

  const filtered = useMemo(() => {
    return MOCK_PAYOUTS.filter(p => 
      !search || p.payoutId.toLowerCase().includes(search.toLowerCase()) || p.merchantId.toLowerCase().includes(search.toLowerCase()) || p.destination.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="payouts">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="MERCHANT DISBURSEMENT CONTROL PLANE"
          title="PAYOUT"
          highlightTitle="OPERATIONS"
          description="Automated merchant bank disbursements, ACH/SEPA/Wire payout scheduling, bank account verification, and payout security."
          icon={ArrowUpRight}
          statusBadge="● PAYOUT ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="secondary" size="sm" onClick={() => alert('Exporting ledger...')}>EXPORT LEDGER</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Schedule Payout Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> SCHEDULE PAYOUT</AGButton>
            </div>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <AGMetricCard label="TOTAL PAYOUTS" value={`${MOCK_PAYOUTS.length}`} subtext="MERCHANT DISBURSEMENTS" accentColor="text-blue-400" />
          <AGMetricCard label="COMPLETED 24H" value="$776.8K" subtext="DISBURSED FLAWLESSLY" accentColor="text-emerald-400" />
          <AGMetricCard label="PROCESSING" value="€508.9K" subtext="ACH / SEPA IN-FLIGHT" accentColor="text-amber-400" />
          <AGMetricCard label="BANK VERIFIED" value="100%" subtext="mTLS + HSM BOUND" accentColor="text-blue-400" />
          <AGMetricCard label="FAILED PAYOUTS" value="00" subtext="ZERO DISBURSEMENT STOPS" accentColor="text-emerald-400" />
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search Payout ID, Merchant, Destination, Bank..."
            className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none"
          />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400 hover:text-slate-200">RESET</button>
        </div>

        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'SCHEDULED', 'PROCESSING', 'COMPLETED', 'FAILED', 'BANK_ACCOUNTS', 'RISK', 'AUDIT'] as PayoutTabType[]).map(t => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {t}
            </button>
          ))}
        </div>

        {activeTab === 'REGISTRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">PAYOUT ID</th>
                  <th className="p-3">MERCHANT ID</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">DESTINATION</th>
                  <th className="p-3">BANK NAME</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3">EXPECTED ARRIVAL</th>
                  <th className="p-3">STATUS</th>
                  <th className="p-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(p => (
                  <tr key={p.id} onClick={() => setSelectedPo(p)} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{p.payoutId}</td>
                    <td className="p-3 text-slate-300">{p.merchantId}</td>
                    <td className="p-3 font-bold text-emerald-400">{p.amount} ({p.currency})</td>
                    <td className="p-3 text-emerald-300 font-bold">{p.destination}</td>
                    <td className="p-3 text-slate-300">{p.bankName}</td>
                    <td className="p-3 font-bold text-purple-400">{p.processor}</td>
                    <td className="p-3 text-slate-400">{p.expectedArrival}</td>
                    <td className="p-3"><AGBadge status={p.status} size="sm" /></td>
                    <td className="p-3 text-right"><button className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 text-[10px]">INSPECT</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab !== 'REGISTRY' && (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">
            {activeTab} OPERATIONAL VIEW ACTIVE — 2 DISBURSEMENTS MONITORED
          </div>
        )}

        {selectedPo && (
          <AGDrawer isOpen={!!selectedPo} onClose={() => setSelectedPo(null)} title={`PAYOUT INSPECTOR: ${selectedPo.payoutId}`} subtitle="MERCHANT BANK DISBURSEMENT">
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded-xl bg-blue-500/5 border border-blue-500/20 space-y-1">
                <div className="text-[9px] text-blue-400 font-bold uppercase">DISBURSEMENT TRACE</div>
                <div className="flex items-center gap-1 text-[10px]">
                  <span className="text-blue-400 font-bold">{selectedPo.merchantId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-purple-400 font-bold">{selectedPo.payoutId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-emerald-400 font-bold">{selectedPo.destination}</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1">
                <div className="flex justify-between"><span className="text-slate-500">Payout Amount:</span><span className="text-emerald-400 font-bold">{selectedPo.amount}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Destination:</span><span className="text-slate-200">{selectedPo.destination} ({selectedPo.bankName})</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Expected Arrival:</span><span className="text-slate-300">{selectedPo.expectedArrival}</span></div>
              </div>
            </div>
          </AGDrawer>
        )}
      </div>
    </AgentPayShell>
  );
}
