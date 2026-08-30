'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { ListFilter, RefreshCw } from 'lucide-react';
import { OrderItemBreakdownTabType } from '@/components/order-item-breakdown/order-item-breakdown-types';
import { MOCK_ORDER_ITEM_BREAKDOWN } from '@/components/order-item-breakdown/order-item-breakdown-data';

export default function OrderItemBreakdownPage() {
  const [activeTab, setActiveTab] = useState<OrderItemBreakdownTabType>('ITEMS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_ORDER_ITEM_BREAKDOWN.filter(i => 
      !search || i.itemId.toLowerCase().includes(search.toLowerCase()) || i.orderRef.toLowerCase().includes(search.toLowerCase()) || i.sku.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="order-item-breakdown">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="GRANULAR ORDER ITEM BREAKDOWN & LINE ALLOCATIONS"
          title="ORDER ITEM"
          highlightTitle="BREAKDOWN"
          description="Granular order item line allocations, unit pricing, SKU tax splits, inventory reservation links, and return eligibility."
          icon={ListFilter}
          statusBadge="● LINE ALLOCATION ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TOTAL LINE ITEMS" value={`${MOCK_ORDER_ITEM_BREAKDOWN.length}`} subtext="ACTIVE ORDER ITEMS" accentColor="text-blue-400" />
          <AGMetricCard label="ALLOCATED VALUE" value="$20,562.09" subtext="LINE TOTALS WITH TAX" accentColor="text-emerald-400" />
          <AGMetricCard label="TOTAL LINE UNITS" value="6 Units" subtext="FULFILLED QUANTITY" accentColor="text-emerald-400" />
          <AGMetricCard label="RETURN ELIGIBILITY" value="50% ELIGIBLE" subtext="POLICY MATCH" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Item ID, Order Ref, SKU..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['ITEMS', 'LINE_TAX', 'DISCOUNT_SPLITS', 'RESERVATIONS', 'RETURNS_ELIGIBILITY', 'AUDIT'] as OrderItemBreakdownTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'ITEMS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">ITEM ID</th>
                  <th className="p-3">ORDER REF</th>
                  <th className="p-3">SKU</th>
                  <th className="p-3">QTY</th>
                  <th className="p-3">UNIT PRICE</th>
                  <th className="p-3">TAX AMOUNT</th>
                  <th className="p-3">LINE TOTAL</th>
                  <th className="p-3">RETURN ELIGIBLE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(i => (
                  <tr key={i.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{i.itemId}</td>
                    <td className="p-3 font-bold text-purple-400">{i.orderRef}</td>
                    <td className="p-3 text-slate-200 font-mono">{i.sku}</td>
                    <td className="p-3 text-slate-400">{i.quantity}</td>
                    <td className="p-3 text-slate-300">{i.unitPrice}</td>
                    <td className="p-3 text-amber-400">{i.taxAmount}</td>
                    <td className="p-3 font-bold text-emerald-400">{i.lineTotal}</td>
                    <td className="p-3 text-emerald-400 font-bold">{i.returnEligible ? 'YES' : 'NO'}</td>
                    <td className="p-3"><AGBadge status={i.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'ITEMS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
