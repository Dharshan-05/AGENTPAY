'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Ticket, RefreshCw, Plus } from 'lucide-react';
import { CouponsTabType } from '@/components/coupons/coupon-types';
import { MOCK_COUPONS } from '@/components/coupons/coupon-data';

export default function CouponsPage() {
  const [activeTab, setActiveTab] = useState<CouponsTabType>('COUPONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_COUPONS.filter(c => 
      !search || c.couponId.toLowerCase().includes(search.toLowerCase()) || c.code.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="coupons">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="COUPON CODE & VOUCHER REDEMPTION ENGINE"
          title="COUPON"
          highlightTitle="CODES"
          description="Autonomous agent promotional coupon codes, single-use vouchers, redemption limits, and agent tracking."
          icon={Ticket}
          statusBadge="● COUPON ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Create Coupon Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> CREATE COUPON</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ACTIVE COUPONS" value={`${MOCK_COUPONS.length}`} subtext="PROMOTIONAL CODES" accentColor="text-blue-400" />
          <AGMetricCard label="TOTAL REDEMPTIONS" value="412" subtext="COUPONS APPLIED" accentColor="text-emerald-400" />
          <AGMetricCard label="SINGLE-USE VOUCHERS" value="1,200" subtext="AGENT VOUCHERS" accentColor="text-emerald-400" />
          <AGMetricCard label="EXHAUSTED CODES" value="01 Code" subtext="LIMIT REACHED" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Coupon ID, Code..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['COUPONS', 'SINGLE_USE', 'VOUCHERS', 'REDEMPTIONS', 'AGENT_CODES', 'LIMITS', 'AUDIT'] as CouponsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'COUPONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">COUPON ID</th>
                  <th className="p-3">PROMO CODE</th>
                  <th className="p-3">TYPE</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">REDEMPTIONS</th>
                  <th className="p-3">MAX LIMIT</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(c => (
                  <tr key={c.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{c.couponId}</td>
                    <td className="p-3 font-bold text-purple-400 font-mono">{c.code}</td>
                    <td className="p-3 text-slate-300">{c.discountType}</td>
                    <td className="p-3 font-bold text-emerald-400">{c.amount}</td>
                    <td className="p-3 text-slate-200">{c.redeemedCount} uses</td>
                    <td className="p-3 text-slate-400">{c.maxRedemptions} max</td>
                    <td className="p-3"><AGBadge status={c.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'COUPONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
