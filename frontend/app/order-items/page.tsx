'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { ListOrdered, RefreshCw } from 'lucide-react';
import { OrderItemsTabType } from '@/components/order-items/order-item-types';
import { MOCK_ORDER_ITEMS } from '@/components/order-items/order-item-data';

export default function OrderItemsPage() {
  const [activeTab, setActiveTab] = useState<OrderItemsTabType>('REGISTRY');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_ORDER_ITEMS.filter(o => 
      !search || o.orderItemId.toLowerCase().includes(search.toLowerCase()) || o.orderId.toLowerCase().includes(search.toLowerCase()) || o.productName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="order-items">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="ORDER ITEMIZATION & TAX ALLOCATION PLANE"
          title="ORDER"
          highlightTitle="ITEMS"
          description="Itemized order line breakdown, SKU reservation mapping, unit pricing, discount allocation, and refund linkage."
          icon={ListOrdered}
          statusBadge="● ITEMIZATION ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TOTAL ORDER ITEMS" value={`${MOCK_ORDER_ITEMS.length}`} subtext="ITEMIZED LINE ITEMS" accentColor="text-blue-400" />
          <AGMetricCard label="COMMITTED ITEMS" value="02" subtext="FULFILLED SKUS" accentColor="text-emerald-400" />
          <AGMetricCard label="LINE ITEM REVENUE" value="$12,999.00" subtext="GROSS ITEMIZED VALUE" accentColor="text-emerald-400" />
          <AGMetricCard label="SKU ACCURACY" value="100%" subtext="ZERO ALLOCATION GAPS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Item ID, Order ID, Product..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'SKUS', 'RESERVATIONS', 'DISCOUNTS', 'TAX_LINES', 'REFUND_LINKAGE', 'AUDIT'] as OrderItemsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'REGISTRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">ORDER ITEM ID</th>
                  <th className="p-3">ORDER ID</th>
                  <th className="p-3">PRODUCT NAME</th>
                  <th className="p-3">SKU</th>
                  <th className="p-3">QUANTITY</th>
                  <th className="p-3">UNIT PRICE</th>
                  <th className="p-3">TOTAL PRICE</th>
                  <th className="p-3">RESERVATION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(o => (
                  <tr key={o.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{o.orderItemId}</td>
                    <td className="p-3 font-bold text-purple-400">{o.orderId}</td>
                    <td className="p-3 font-bold text-slate-200">{o.productName}</td>
                    <td className="p-3 text-slate-300">{o.sku}</td>
                    <td className="p-3 text-slate-300">{o.quantity}x</td>
                    <td className="p-3 text-slate-400">{o.unitPrice}</td>
                    <td className="p-3 font-bold text-emerald-400">{o.totalPrice}</td>
                    <td className="p-3"><AGBadge status={o.reservationStatus} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'REGISTRY' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
