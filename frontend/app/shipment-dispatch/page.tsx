'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Truck, RefreshCw } from 'lucide-react';
import { ShipmentDispatchTabType } from '@/components/shipment-dispatch/shipment-dispatch-types';
import { MOCK_SHIPMENT_DISPATCH } from '@/components/shipment-dispatch/shipment-dispatch-data';

export default function ShipmentDispatchPage() {
  const [activeTab, setActiveTab] = useState<ShipmentDispatchTabType>('SHIPMENTS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SHIPMENT_DISPATCH.filter(s => 
      !search || s.dispatchId.toLowerCase().includes(search.toLowerCase()) || s.orderRef.toLowerCase().includes(search.toLowerCase()) || s.trackingNumber.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="shipment-dispatch">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="MULTI-CARRIER LOGISTICS DISPATCH & TRACKING PLANE"
          title="SHIPMENT"
          highlightTitle="DISPATCH"
          description="Automated carrier shipment dispatch, tracking feed telemetry, route exception handling, and proof-of-delivery verification."
          icon={Truck}
          statusBadge="● DISPATCH ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TOTAL SHIPMENTS" value={`${MOCK_SHIPMENT_DISPATCH.length}`} subtext="ACTIVE LOGISTICS ROUTING" accentColor="text-blue-400" />
          <AGMetricCard label="CARRIER NETWORK" value="03 Carriers" subtext="FEDEX / DHL / UPS" accentColor="text-emerald-400" />
          <AGMetricCard label="ON-TIME DELIVERY SLA" value="99.8%" subtext="SCHEDULE MATCH" accentColor="text-emerald-400" />
          <AGMetricCard label="ROUTE EXCEPTIONS" value="00 Stopped" subtext="ZERO DELAYS DETECTED" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Dispatch ID, Order Ref, Tracking..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['SHIPMENTS', 'CARRIERS', 'TRACKING_FEEDS', 'DISPATCH_RULES', 'EXCEPTIONS', 'AUDIT'] as ShipmentDispatchTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'SHIPMENTS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">DISPATCH ID</th>
                  <th className="p-3">ORDER REF</th>
                  <th className="p-3">CARRIER</th>
                  <th className="p-3">TRACKING NO</th>
                  <th className="p-3">ORIGIN → DESTINATION</th>
                  <th className="p-3">EST DELIVERY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.dispatchId}</td>
                    <td className="p-3 font-bold text-purple-400">{s.orderRef}</td>
                    <td className="p-3 text-slate-200">{s.carrier}</td>
                    <td className="p-3 font-bold text-emerald-400 font-mono">{s.trackingNumber}</td>
                    <td className="p-3 text-slate-300">{s.origin} → {s.destination}</td>
                    <td className="p-3 text-slate-400">{s.estimatedDelivery}</td>
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
