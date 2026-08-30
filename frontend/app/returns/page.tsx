'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { RotateCcw, RefreshCw } from 'lucide-react';
import { ReturnsTabType } from '@/components/returns/return-types';
import { MOCK_RETURNS } from '@/components/returns/return-data';

export default function ReturnsPage() {
  const [activeTab, setActiveTab] = useState<ReturnsTabType>('REQUESTS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_RETURNS.filter(r => 
      !search || r.rmaId.toLowerCase().includes(search.toLowerCase()) || r.orderId.toLowerCase().includes(search.toLowerCase()) || r.customer.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="returns">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="RETURN MERCHANDISE AUTHORIZATION (RMA) PLANE"
          title="PRODUCT"
          highlightTitle="RETURNS (RMA)"
          description="RMA workflow management, return inspection status, store credit / refund processing, and defect telemetry."
          icon={RotateCcw}
          statusBadge="● RMA ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="RMA REQUESTS" value={`${MOCK_RETURNS.length}`} subtext="ACTIVE RETURN ORDERS" accentColor="text-blue-400" />
          <AGMetricCard label="INSPECTION PASS RATE" value="99.2%" subtext="PASSED QUALITY CHECK" accentColor="text-emerald-400" />
          <AGMetricCard label="REFUNDED VALUE" value="$499.00" subtext="PROCESSED REFUNDS" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG RMA TURNAROUND" value="1.2 Days" subtext="TARGET < 2 DAYS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search RMA ID, Order ID, Customer..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REQUESTS', 'APPROVED', 'IN_INSPECTION', 'REFUNDED', 'REJECTED', 'REASON_CODES', 'AUDIT'] as ReturnsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'REQUESTS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">RMA ID</th>
                  <th className="p-3">ORDER ID</th>
                  <th className="p-3">CUSTOMER</th>
                  <th className="p-3">REASON</th>
                  <th className="p-3">REFUND AMOUNT</th>
                  <th className="p-3">INSPECTION</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(r => (
                  <tr key={r.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{r.rmaId}</td>
                    <td className="p-3 font-bold text-purple-400">{r.orderId}</td>
                    <td className="p-3 font-bold text-slate-200">{r.customer}</td>
                    <td className="p-3 text-slate-300">{r.reason}</td>
                    <td className="p-3 font-bold text-emerald-400">{r.refundAmount}</td>
                    <td className="p-3 text-emerald-400 font-bold">{r.inspectionState}</td>
                    <td className="p-3"><AGBadge status={r.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'REQUESTS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
