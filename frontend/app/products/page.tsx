'use client';
import { useState, useMemo, useEffect } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Package, RefreshCw, Plus, Check } from 'lucide-react';
import { ProductsTabType } from '@/components/products/product-types';
import { MOCK_PRODUCTS } from '@/components/products/product-data';
import { getSharedCommerceState, saveSharedCommerceState, addToCart } from '@/lib/commerce-store';

export default function ProductsPage() {
  const [activeTab, setActiveTab] = useState<ProductsTabType>('CATALOG');
  const [search, setSearch] = useState('');
  const [sharedState, setSharedState] = useState<any>(() => getSharedCommerceState());

  useEffect(() => {
    const handleUpdate = () => {
      setSharedState(getSharedCommerceState());
    };
    if (typeof window !== 'undefined') {
      window.addEventListener('agentpay_commerce_session_updated', handleUpdate);
      return () => window.removeEventListener('agentpay_commerce_session_updated', handleUpdate);
    }
  }, []);

  const combinedProducts = useMemo(() => {
    const sessionItems = (sharedState?.products || []).map((p: any, idx: number) => ({
      id: p.product_id || `session_${idx}`,
      productId: p.product_id || `PROD-${idx + 1}`,
      name: p.product_name,
      sku: `SKU-LIVE-${p.product_id ? p.product_id.slice(-6).toUpperCase() : idx + 1}`,
      type: p.category || 'COMMERCE',
      price: `₹${Number(p.price).toLocaleString('en-IN')}`,
      rawPrice: Number(p.price),
      currency: p.currency || 'INR',
      taxCategory: 'STANDARD_GST_18',
      status: sharedState?.selected_product_id === p.product_id ? 'ACTIVE' : 'READY',
      originalProduct: p,
    }));
    return [...sessionItems, ...MOCK_PRODUCTS];
  }, [sharedState]);

  const filtered = useMemo(() => {
    return combinedProducts.filter(p => 
      !search || p.productId.toLowerCase().includes(search.toLowerCase()) || p.name.toLowerCase().includes(search.toLowerCase()) || p.sku.toLowerCase().includes(search.toLowerCase())
    );
  }, [combinedProducts, search]);

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
              <AGButton variant="ghost" size="sm" onClick={() => setSharedState(getSharedCommerceState())}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => window.location.href = '/ai-command-center'}><Plus className="w-3.5 h-3.5 mr-1.5" /> SEARCH PRODUCTS</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="CATALOG PRODUCTS" value={`${combinedProducts.length}`} subtext="ACTIVE SKU ITEMS" accentColor="text-blue-400" />
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
                  <th className="p-3">STATUS</th>
                  <th className="p-3">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(p => (
                  <tr key={p.id} className="hover:bg-slate-900/40">
                    <td className="p-3 font-bold text-blue-400">{p.productId}</td>
                    <td className="p-3 font-bold text-slate-200">{p.name}</td>
                    <td className="p-3 font-bold text-purple-400">{p.sku}</td>
                    <td className="p-3 text-slate-300">{p.type}</td>
                    <td className="p-3 font-bold text-emerald-400">{p.price} ({p.currency})</td>
                    <td className="p-3"><AGBadge status={p.status} size="sm" /></td>
                    <td className="p-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => {
                            const prodObj = p.originalProduct || {
                              product_id: p.productId,
                              product_name: p.name,
                              price: p.rawPrice || 44990,
                              currency: p.currency || 'INR',
                              seller: { seller_id: 'seller_appario_retail', seller_name: 'Appario Retail' },
                            };
                            saveSharedCommerceState({
                              selected_product: prodObj,
                              selected_product_id: prodObj.product_id,
                              purchase_state: 'SELECTED',
                              current_price: Number(prodObj.price),
                            });
                            setSharedState(getSharedCommerceState());
                          }}
                          className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/30 font-bold"
                        >
                          {sharedState?.selected_product_id === (p.originalProduct?.product_id || p.productId) ? 'SELECTED ✓' : '[SELECT]'}
                        </button>

                        <button
                          onClick={() => {
                            const prodObj = p.originalProduct || {
                              product_id: p.productId,
                              product_name: p.name,
                              price: p.rawPrice || 44990,
                              currency: p.currency || 'INR',
                              seller: { seller_id: 'seller_appario_retail', seller_name: 'Appario Retail' },
                            };
                            const updated = addToCart(prodObj);
                            setSharedState(updated);
                            alert(`Added ${p.name} to AGENTPAY Cart.`);
                          }}
                          className="px-2.5 py-1 rounded bg-blue-500/20 text-blue-300 hover:bg-blue-500/30 border border-blue-500/30 font-bold"
                        >
                          [ADD TO CART]
                        </button>
                      </div>
                    </td>
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
