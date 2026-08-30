'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Truck, RefreshCw } from 'lucide-react';
import { ShippingTabType } from '@/components/shipping/shipping-types';
import { MOCK_SHIPPING } from '@/components/shipping/shipping-data';

export default function ShippingPage() {
  const [activeTab, setActiveTab] = useState<ShippingTabType>('SHIPMENTS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SHIPPING.filter(s => 
      !search || s.shipmentId.toLowerCase().includes(search.toLowerCase()) || s.orderId.toLowerCase().includes(search.toLowerCase()) || s.trackingId.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="shipping">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="CARRIER SHIPPING & PARCEL TRACKING PLANE"
          title="SHIPPING"
          highlightTitle="OPERATIONS"
          description="Multi-carrier shipment dispatch, real-time parcel tracking telemetry, label generation, and delivery SLA verification."
          icon={Truck}
          statusBadge="● CARRIER DISPATCH ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TOTAL SHIPMENTS" value={`${MOCK_SHIPPING.length}`} subtext="ACTIVE PARCELS" accentColor="text-blue-400" />
          <AGMetricCard label="ON-TIME DELIVERY" value="99.8%" subtext="CARRIER SLA MET" accentColor="text-emerald-400" />
          <AGMetricCard label="DELIVERED PARCELS" value="01" subtext="CONFIRMED RECEIPT" accentColor="text-emerald-400" />
          <AGMetricCard label="EXCEPTIONS" value="00" subtext="ZERO LOST SHIPMENTS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Shipment ID, Order ID, Tracking..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['SHIPMENTS', 'CARRIERS', 'LABEL_GENERATION', 'IN_TRANSIT', 'DELIVERED', 'EXCEPTIONS', 'AUDIT'] as ShippingTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'SHIPMENTS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SHIPMENT ID</th>
                  <th className="p-3">ORDER ID</th>
                  <th className="p-3">CARRIER</th>
                  <th className="p-3">SERVICE</th>
                  <th className="p-3">TRACKING ID</th>
                  <th className="p-3">DESTINATION</th>
                  <th className="p-3">COST</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.shipmentId}</td>
                    <td className="p-3 font-bold text-purple-400">{s.orderId}</td>
                    <td className="p-3 font-bold text-slate-200">{s.carrier}</td>
                    <td className="p-3 text-slate-300">{s.service}</td>
                    <td className="p-3 text-slate-400 font-mono text-[10px]">{s.trackingId}</td>
                    <td className="p-3 text-slate-300">{s.destination}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.shippingCost}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'SHIPMENTS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
