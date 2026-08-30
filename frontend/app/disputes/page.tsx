'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { AlertCircle, RefreshCw, Download, Upload, ArrowRight } from 'lucide-react';
import { DisputeTabType, DisputeRecord } from '@/components/disputes/dispute-types';
import { MOCK_DISPUTES } from '@/components/disputes/dispute-data';

export default function DisputesPage() {
  const [activeTab, setActiveTab] = useState<DisputeTabType>('REGISTRY');
  const [search, setSearch] = useState('');
  const [selectedDsp, setSelectedDsp] = useState<DisputeRecord | null>(null);

  const filtered = useMemo(() => {
    return MOCK_DISPUTES.filter(d => 
      !search || d.disputeId.toLowerCase().includes(search.toLowerCase()) || d.transactionId.toLowerCase().includes(search.toLowerCase()) || d.customer.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="disputes">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="CHARGEBACK & DISPUTE RESOLUTION PLANE"
          title="DISPUTE"
          highlightTitle="OPERATIONS"
          description="Automated evidence compilation, network chargeback response, dispute deadline tracking, and FraudGuard defense automation."
          icon={AlertCircle}
          statusBadge="● DISPUTE ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="secondary" size="sm" onClick={() => alert('Exporting ledger...')}>EXPORT LEDGER</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Submit Evidence Flow')}><Upload className="w-3.5 h-3.5 mr-1.5" /> SUBMIT EVIDENCE</AGButton>
            </div>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <AGMetricCard label="OPEN DISPUTES" value={`${MOCK_DISPUTES.length}`} subtext="ACTIVE CHARGEBACKS" accentColor="text-rose-400" />
          <AGMetricCard label="DISPUTED AMOUNT" value="$2,470.00" subtext="AT-RISK CAPITAL" accentColor="text-rose-400" />
          <AGMetricCard label="NEEDS RESPONSE" value="01" subtext="ACTION REQUIRED" accentColor="text-amber-400" />
          <AGMetricCard label="UNDER REVIEW" value="01" subtext="SUBMITTED TO NETWORK" accentColor="text-blue-400" />
          <AGMetricCard label="WIN RATE" value="88.4%" subtext="HISTORICAL SUCCESS" accentColor="text-emerald-400" />
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search Dispute ID, Transaction ID, Customer, Reason..."
            className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none"
          />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400 hover:text-slate-200">RESET</button>
        </div>

        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'OPEN', 'EVIDENCE', 'CHARGEBACKS', 'RESPONSES', 'RESOLUTION', 'RISK', 'AUDIT'] as DisputeTabType[]).map(t => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' : 'text-slate-400 hover:text-slate-200'}`}
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
                  <th className="p-3">DISPUTE ID</th>
                  <th className="p-3">TXN ID</th>
                  <th className="p-3">CUSTOMER</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">REASON</th>
                  <th className="p-3">NETWORK</th>
                  <th className="p-3">DEADLINE</th>
                  <th className="p-3">STATUS</th>
                  <th className="p-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(d => (
                  <tr key={d.id} onClick={() => setSelectedDsp(d)} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-rose-400">{d.disputeId}</td>
                    <td className="p-3 font-bold text-blue-400">{d.transactionId}</td>
                    <td className="p-3 text-slate-300">{d.customer}</td>
                    <td className="p-3 font-bold text-rose-300">{d.amount} ({d.currency})</td>
                    <td className="p-3 text-slate-300">{d.reason}</td>
                    <td className="p-3 font-bold text-purple-400">{d.network}</td>
                    <td className="p-3 text-amber-400 font-bold">{d.deadline}</td>
                    <td className="p-3"><AGBadge status={d.status} size="sm" /></td>
                    <td className="p-3 text-right"><button className="px-2 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px]">INSPECT</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab !== 'REGISTRY' && (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">
            {activeTab} OPERATIONAL VIEW ACTIVE — 2 CHARGEBACK CASES MONITORED
          </div>
        )}

        {selectedDsp && (
          <AGDrawer isOpen={!!selectedDsp} onClose={() => setSelectedDsp(null)} title={`DISPUTE INSPECTOR: ${selectedDsp.disputeId}`} subtitle="CHARGEBACK EVIDENCE DEFENSE">
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded-xl bg-rose-500/5 border border-rose-500/20 space-y-1">
                <div className="text-[9px] text-rose-400 font-bold uppercase">DISPUTE CAUSAL TRACE</div>
                <div className="flex items-center gap-1 text-[10px]">
                  <span className="text-blue-400 font-bold">{selectedDsp.transactionId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-purple-400 font-bold">{selectedDsp.network}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-rose-400 font-bold">{selectedDsp.disputeId}</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1">
                <div className="flex justify-between"><span className="text-slate-500">Disputed Amount:</span><span className="text-rose-400 font-bold">{selectedDsp.amount}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Reason:</span><span className="text-slate-200">{selectedDsp.reason}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Response Deadline:</span><span className="text-amber-400 font-bold">{selectedDsp.deadline}</span></div>
              </div>
            </div>
          </AGDrawer>
        )}
      </div>
    </AgentPayShell>
  );
}
