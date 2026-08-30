'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Boxes, RefreshCw } from 'lucide-react';
import { InventoryTabType } from '@/components/inventory/inventory-types';
import { MOCK_INVENTORY } from '@/components/inventory/inventory-data';

export default function InventoryPage() {
  const [activeTab, setActiveTab] = useState<InventoryTabType>('STOCK_LEVELS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_INVENTORY.filter(i => 
      !search || i.inventoryId.toLowerCase().includes(search.toLowerCase()) || i.sku.toLowerCase().includes(search.toLowerCase()) || i.productName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="inventory">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="MULTI-WAREHOUSE INVENTORY & STOCK CONTROL PLANE"
          title="INVENTORY &"
          highlightTitle="STOCK"
          description="Enterprise multi-warehouse inventory levels, SKU availability tracking, low-stock reorder alerts, and stock health monitoring."
          icon={Boxes}
          statusBadge="● INVENTORY SYNCED"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="INVENTORY SKUS" value={`${MOCK_INVENTORY.length}`} subtext="MONITORED ITEMS" accentColor="text-blue-400" />
          <AGMetricCard label="AVAILABLE UNITS" value="862 Units" subtext="READY FOR ALLOCATION" accentColor="text-emerald-400" />
          <AGMetricCard label="RESERVED UNITS" value="52 Units" subtext="ORDER IN-FLIGHT" accentColor="text-amber-400" />
          <AGMetricCard label="LOW STOCK ALERTS" value="01 SKU" subtext="REORDER NEEDED" accentColor="text-rose-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Inventory ID, SKU, Product..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['STOCK_LEVELS', 'WAREHOUSES', 'RESERVATIONS', 'REORDER_ALERTS', 'HEALTH', 'MOVEMENTS', 'AUDIT'] as InventoryTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'STOCK_LEVELS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">INVENTORY ID</th>
                  <th className="p-3">SKU</th>
                  <th className="p-3">PRODUCT NAME</th>
                  <th className="p-3">WAREHOUSE</th>
                  <th className="p-3">AVAILABLE</th>
                  <th className="p-3">RESERVED</th>
                  <th className="p-3">HEALTH</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(i => (
                  <tr key={i.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{i.inventoryId}</td>
                    <td className="p-3 font-bold text-purple-400">{i.sku}</td>
                    <td className="p-3 font-bold text-slate-200">{i.productName}</td>
                    <td className="p-3 text-slate-300">{i.warehouse}</td>
                    <td className="p-3 font-bold text-emerald-400">{i.available} units</td>
                    <td className="p-3 text-amber-400 font-bold">{i.reserved} units</td>
                    <td className="p-3"><AGBadge status={i.healthState} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'STOCK_LEVELS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
