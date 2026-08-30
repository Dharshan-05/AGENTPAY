'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Clock, RefreshCw } from 'lucide-react';
import { StockReservationsTabType } from '@/components/stock-reservations/stock-reservation-types';
import { MOCK_STOCK_RESERVATIONS } from '@/components/stock-reservations/stock-reservation-data';

export default function StockReservationsPage() {
  const [activeTab, setActiveTab] = useState<StockReservationsTabType>('RESERVATIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_STOCK_RESERVATIONS.filter(s => 
      !search || s.reservationId.toLowerCase().includes(search.toLowerCase()) || s.orderRef.toLowerCase().includes(search.toLowerCase()) || s.sku.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="stock-reservations">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="STOCK RESERVATION & TTL ALLOCATION CONTROL PLANE"
          title="STOCK"
          highlightTitle="RESERVATIONS"
          description="Autonomous agent inventory reservations, TTL countdown monitoring, auto-release triggers, and fulfillment binding."
          icon={Clock}
          statusBadge="● RESERVATION ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ACTIVE RESERVATIONS" value={`${MOCK_STOCK_RESERVATIONS.length}`} subtext="HOLDING INVENTORY" accentColor="text-blue-400" />
          <AGMetricCard label="RESERVED QUANTITY" value="6 Units" subtext="TOTAL HELD UNITS" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG TTL HOLD" value="15 Mins" subtext="AUTO-RELEASE TTL" accentColor="text-emerald-400" />
          <AGMetricCard label="RELEASE RATE" value="0% EXPIRED" subtext="100% CONVERSION TO ORDER" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Reservation ID, Order Ref, SKU..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['RESERVATIONS', 'TTL_MONITOR', 'EXPIRATIONS', 'RELEASED', 'FULFILLED', 'AUDIT'] as StockReservationsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'RESERVATIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">RESERVATION ID</th>
                  <th className="p-3">ORDER REF</th>
                  <th className="p-3">SKU</th>
                  <th className="p-3">QTY</th>
                  <th className="p-3">TTL REMAINING</th>
                  <th className="p-3">WAREHOUSE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.reservationId}</td>
                    <td className="p-3 font-bold text-purple-400">{s.orderRef}</td>
                    <td className="p-3 text-slate-200 font-mono">{s.sku}</td>
                    <td className="p-3 text-slate-400">{s.quantity}</td>
                    <td className="p-3 text-amber-400 font-bold">{s.ttlRemainingMinutes > 0 ? `${s.ttlRemainingMinutes} mins` : 'EXPIRED / FULFILLED'}</td>
                    <td className="p-3 text-slate-300">{s.warehouse}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'RESERVATIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
