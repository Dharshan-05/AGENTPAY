'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Boxes, RefreshCw } from 'lucide-react';
import { InventoryControlTabType } from '@/components/inventory-control/inventory-control-types';
import { MOCK_INVENTORY_CONTROL } from '@/components/inventory-control/inventory-control-data';

export default function InventoryControlPage() {
  const [activeTab, setActiveTab] = useState<InventoryControlTabType>('WAREHOUSES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_INVENTORY_CONTROL.filter(i => 
      !search || i.inventoryId.toLowerCase().includes(search.toLowerCase()) || i.warehouseLocation.toLowerCase().includes(search.toLowerCase()) || i.sku.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="inventory-control">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="MULTI-LOCATION INVENTORY CONTROL & STOCK HEALTH PLANE"
          title="INVENTORY"
          highlightTitle="CONTROL"
          description="Multi-warehouse inventory control, real-time available vs reserved units, reorder threshold triggers, and stock movement logs."
          icon={Boxes}
          statusBadge="● STOCK HEALTH ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="WAREHOUSE LOCATIONS" value={`${MOCK_INVENTORY_CONTROL.length}`} subtext="ACTIVE FULFILLMENT HUBS" accentColor="text-blue-400" />
          <AGMetricCard label="TOTAL AVAILABLE UNITS" value="1,465 Units" subtext="UNRESERVED STOCK" accentColor="text-emerald-400" />
          <AGMetricCard label="RESERVED UNITS" value="95 Units" subtext="PENDING FULFILLMENT" accentColor="text-emerald-400" />
          <AGMetricCard label="STOCK HEALTH" value="98.5% HEALTHY" subtext="01 WAREHOUSE REORDER" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Inventory ID, Warehouse, SKU..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['WAREHOUSES', 'STOCK_HEALTH', 'MOVEMENTS', 'REORDER_THRESHOLDS', 'DAMAGED', 'AUDIT'] as InventoryControlTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'WAREHOUSES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">INVENTORY ID</th>
                  <th className="p-3">WAREHOUSE LOCATION</th>
                  <th className="p-3">SKU</th>
                  <th className="p-3">AVAILABLE UNITS</th>
                  <th className="p-3">RESERVED UNITS</th>
                  <th className="p-3">REORDER LEVEL</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(i => (
                  <tr key={i.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{i.inventoryId}</td>
                    <td className="p-3 font-bold text-slate-200">{i.warehouseLocation}</td>
                    <td className="p-3 font-bold text-purple-400 font-mono">{i.sku}</td>
                    <td className="p-3 font-bold text-emerald-400">{i.availableUnits} units</td>
                    <td className="p-3 text-amber-400">{i.reservedUnits} units</td>
                    <td className="p-3 text-slate-400">{i.reorderLevel} units</td>
                    <td className="p-3"><AGBadge status={i.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'WAREHOUSES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
