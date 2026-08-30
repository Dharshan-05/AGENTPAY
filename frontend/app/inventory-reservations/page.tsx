'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Clock, RefreshCw } from 'lucide-react';
import { ReservationsTabType } from '@/components/inventory-reservations/inventory-reservation-types';
import { MOCK_RESERVATIONS } from '@/components/inventory-reservations/inventory-reservation-data';

export default function InventoryReservationsPage() {
  const [activeTab, setActiveTab] = useState<ReservationsTabType>('ACTIVE');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_RESERVATIONS.filter(r => 
      !search || r.reservationId.toLowerCase().includes(search.toLowerCase()) || r.orderId.toLowerCase().includes(search.toLowerCase()) || r.sku.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="inventory-reservations">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="TTL-BACKED INVENTORY RESERVATION ENGINE"
          title="INVENTORY"
          highlightTitle="RESERVATIONS"
          description="Ephemeral stock reservation tracking, 30-minute checkout TTL expiry, automatic stock release, and order allocation."
          icon={Clock}
          statusBadge="● RESERVATION LOCK ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="RESERVATIONS" value={`${MOCK_RESERVATIONS.length}`} subtext="ACTIVE LOCKS" accentColor="text-blue-400" />
          <AGMetricCard label="TTL CONVERSION" value="98.4%" subtext="COMMITTED TO ORDERS" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG LOCK TIME" value="4.2m" subtext="TARGET < 30M" accentColor="text-emerald-400" />
          <AGMetricCard label="AUTO-RELEASED" value="00" subtext="ZERO TIMEOUT LEAKS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Reservation ID, Order ID, SKU..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['ACTIVE', 'EXPIRING', 'COMMITTED', 'RELEASED', 'EXPIRED', 'TIMELINE', 'AUDIT'] as ReservationsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'ACTIVE' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">RESERVATION ID</th>
                  <th className="p-3">ORDER ID</th>
                  <th className="p-3">SKU</th>
                  <th className="p-3">QUANTITY</th>
                  <th className="p-3">RESERVED AT</th>
                  <th className="p-3">EXPIRES AT</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(r => (
                  <tr key={r.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{r.reservationId}</td>
                    <td className="p-3 font-bold text-purple-400">{r.orderId}</td>
                    <td className="p-3 text-slate-200">{r.sku}</td>
                    <td className="p-3 text-slate-300">{r.quantity}x</td>
                    <td className="p-3 text-slate-400">{r.reservedAt}</td>
                    <td className="p-3 text-amber-400 font-bold">{r.expiresAt}</td>
                    <td className="p-3"><AGBadge status={r.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'ACTIVE' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
