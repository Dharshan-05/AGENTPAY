'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Package, RefreshCw, Plus } from 'lucide-react';
import { ProductsTabType } from '@/components/products/product-types';
import { MOCK_PRODUCTS } from '@/components/products/product-data';

export default function ProductsPage() {
  const [activeTab, setActiveTab] = useState<ProductsTabType>('CATALOG');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_PRODUCTS.filter(p => 
      !search || p.productId.toLowerCase().includes(search.toLowerCase()) || p.name.toLowerCase().includes(search.toLowerCase()) || p.sku.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="products">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="PRODUCT CATALOG & SKU OPERATIONS PLANE"
          title="PRODUCT"
          highlightTitle="CATALOG"
          description="Autonomous agent product SKU management, digital service pricing, multi-currency price lists, tax category mapping, and merchant catalog sync."
          icon={Package}
          statusBadge="● PRODUCT CATALOG ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Add Product Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> ADD PRODUCT</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="CATALOG PRODUCTS" value={`${MOCK_PRODUCTS.length}`} subtext="ACTIVE SKU ITEMS" accentColor="text-blue-400" />
          <AGMetricCard label="DIGITAL SERVICES" value="02" subtext="SOFTWARE & API SKU" accentColor="text-emerald-400" />
          <AGMetricCard label="TAX CATEGORIES" value="VERIFIED" subtext="AUTOMATED VAT/GST MAPPING" accentColor="text-emerald-400" />
          <AGMetricCard label="MERCHANT SYNC" value="100%" subtext="MULTI-CATALOG BINDING" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Product ID, SKU, Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['CATALOG', 'SKUS', 'PRICING', 'TAX_CATEGORIES', 'INVENTORY', 'MERCHANTS', 'AUDIT'] as ProductsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'CATALOG' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">PRODUCT ID</th>
                  <th className="p-3">PRODUCT NAME</th>
                  <th className="p-3">SKU</th>
                  <th className="p-3">TYPE</th>
                  <th className="p-3">PRICE</th>
                  <th className="p-3">TAX CATEGORY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(p => (
                  <tr key={p.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{p.productId}</td>
                    <td className="p-3 font-bold text-slate-200">{p.name}</td>
                    <td className="p-3 font-bold text-purple-400">{p.sku}</td>
                    <td className="p-3 text-slate-300">{p.type}</td>
                    <td className="p-3 font-bold text-emerald-400">{p.price} ({p.currency})</td>
                    <td className="p-3 text-slate-400">{p.taxCategory}</td>
                    <td className="p-3"><AGBadge status={p.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'CATALOG' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
