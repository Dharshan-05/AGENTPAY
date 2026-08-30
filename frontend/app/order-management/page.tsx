'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { ShoppingBag, RefreshCw } from 'lucide-react';
import { OrderManagementTabType } from '@/components/order-management/order-management-types';
import { MOCK_ORDER_MANAGEMENT } from '@/components/order-management/order-management-data';

export default function OrderManagementPage() {
  const [activeTab, setActiveTab] = useState<OrderManagementTabType>('ORDERS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_ORDER_MANAGEMENT.filter(o => 
      !search || o.orderId.toLowerCase().includes(search.toLowerCase()) || o.customerRef.toLowerCase().includes(search.toLowerCase()) || o.agentRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="order-management">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="ENTERPRISE ORDER MANAGEMENT & FULFILLMENT MATRIX"
          title="ORDER"
          highlightTitle="MANAGEMENT"
          description="Autonomous agent order orchestration, payment & fulfillment matrix tracking, customer/merchant binding, and SLA verification."
          icon={ShoppingBag}
          statusBadge="● ORDER MANAGEMENT ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TOTAL MANAGED ORDERS" value={`${MOCK_ORDER_MANAGEMENT.length}`} subtext="ACTIVE ORDER PIPELINES" accentColor="text-blue-400" />
          <AGMetricCard label="MANAGED VOLUME" value="$18.59K" subtext="TOTAL MANAGED VALUE" accentColor="text-emerald-400" />
          <AGMetricCard label="FULFILLMENT SLA" value="100%" subtext="SUB-24H FULFILLMENT" accentColor="text-emerald-400" />
          <AGMetricCard label="AGENT ORIGINATED" value="100%" subtext="AUTONOMOUS AGENT ORDERS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Order ID, Customer, Agent..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['ORDERS', 'FULFILLMENT_MATRIX', 'PAYMENT_STATES', 'AGENT_ORIGINATED', 'COMPLETED', 'CANCELLED', 'AUDIT'] as OrderManagementTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'ORDERS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">ORDER ID</th>
                  <th className="p-3">CUSTOMER REF</th>
                  <th className="p-3">MERCHANT REF</th>
                  <th className="p-3">AGENT REF</th>
                  <th className="p-3">TOTAL VALUE</th>
                  <th className="p-3">PAYMENT STATE</th>
                  <th className="p-3">FULFILLMENT</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(o => (
                  <tr key={o.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{o.orderId}</td>
                    <td className="p-3 text-slate-200">{o.customerRef}</td>
                    <td className="p-3 text-slate-300">{o.merchantRef}</td>
                    <td className="p-3 font-bold text-purple-400">{o.agentRef}</td>
                    <td className="p-3 font-bold text-emerald-400">{o.totalValue}</td>
                    <td className="p-3"><AGBadge status={o.paymentState} size="sm" /></td>
                    <td className="p-3 text-emerald-400 font-bold">{o.fulfillmentState}</td>
                    <td className="p-3"><AGBadge status={o.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'ORDERS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
