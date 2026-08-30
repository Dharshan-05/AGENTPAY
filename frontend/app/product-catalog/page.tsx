'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Layers, RefreshCw, Plus } from 'lucide-react';
import { ProductCatalogTabType } from '@/components/product-catalog/product-catalog-types';
import { MOCK_PRODUCT_CATALOG } from '@/components/product-catalog/product-catalog-data';

export default function ProductCatalogPage() {
  const [activeTab, setActiveTab] = useState<ProductCatalogTabType>('CATALOG_MATRIX');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_PRODUCT_CATALOG.filter(p => 
      !search || p.catalogId.toLowerCase().includes(search.toLowerCase()) || p.productName.toLowerCase().includes(search.toLowerCase()) || p.skuVariant.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="product-catalog">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="PRODUCT CATALOG & ADVANCED VARIANTS CONTROL PLANE"
          title="PRODUCT"
          highlightTitle="CATALOG MATRIX"
          description="Autonomous agent product catalog variants, multi-option SKU matrices, multi-currency price bounds, and AgentGuard policy eligibility."
          icon={Layers}
          statusBadge="● CATALOG ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Add Catalog Item Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> ADD CATALOG ITEM</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="CATALOG ITEMS" value={`${MOCK_PRODUCT_CATALOG.length}`} subtext="ACTIVE SKU VARIANTS" accentColor="text-blue-400" />
          <AGMetricCard label="AGENT ELIGIBILITY" value="100% ELIGIBLE" subtext="AGENTGUARD VERIFIED" accentColor="text-emerald-400" />
          <AGMetricCard label="MULTI-CURRENCY" value="12 Currencies" subtext="AUTOMATED FX CONVERSION" accentColor="text-emerald-400" />
          <AGMetricCard label="RISK CLASSIFICATION" value="LOW RISK" subtext="ZERO AUDIT GAPS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Catalog ID, Product, SKU..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['CATALOG_MATRIX', 'VARIANTS', 'MULTI_CURRENCY', 'TAX_PROFILES', 'AGENT_ELIGIBILITY', 'AUDIT'] as ProductCatalogTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'CATALOG_MATRIX' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">CATALOG ID</th>
                  <th className="p-3">PRODUCT NAME</th>
                  <th className="p-3">SKU VARIANT</th>
                  <th className="p-3">CATEGORY</th>
                  <th className="p-3">BASE PRICE (USD)</th>
                  <th className="p-3">AGENT ELIGIBLE</th>
                  <th className="p-3">RISK TIER</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(p => (
                  <tr key={p.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{p.catalogId}</td>
                    <td className="p-3 font-bold text-slate-200">{p.productName}</td>
                    <td className="p-3 font-bold text-purple-400">{p.skuVariant}</td>
                    <td className="p-3 text-slate-300">{p.category}</td>
                    <td className="p-3 font-bold text-emerald-400">{p.basePriceUSD}</td>
                    <td className="p-3 text-emerald-400 font-bold">{p.agentEligible ? 'YES' : 'NO'}</td>
                    <td className="p-3 text-slate-300 font-bold">{p.riskTier}</td>
                    <td className="p-3"><AGBadge status={p.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'CATALOG_MATRIX' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
