'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Gift, RefreshCw, Plus } from 'lucide-react';
import { GiftCardsTabType } from '@/components/gift-cards/gift-card-types';
import { MOCK_GIFT_CARDS } from '@/components/gift-cards/gift-card-data';

export default function GiftCardsPage() {
  const [activeTab, setActiveTab] = useState<GiftCardsTabType>('CARDS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_GIFT_CARDS.filter(g => 
      !search || g.giftCardId.toLowerCase().includes(search.toLowerCase()) || g.recipient.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="gift-cards">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="GIFT CARD & PREPAID STORED VALUE LEDGER"
          title="GIFT"
          highlightTitle="CARDS"
          description="Encrypted stored value gift cards, digital prepaid balances, pin-vault security, and transaction redemption tracking."
          icon={Gift}
          statusBadge="● STORED VALUE VAULT ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Issue Gift Card Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> ISSUE GIFT CARD</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="GIFT CARDS ISSUED" value={`${MOCK_GIFT_CARDS.length}`} subtext="ACTIVE STORED VALUE" accentColor="text-blue-400" />
          <AGMetricCard label="TOTAL VAULT VALUE" value="$1,150.00" subtext="CURRENT BALANCES" accentColor="text-emerald-400" />
          <AGMetricCard label="REDEEMED VOLUME" value="$350.00" subtext="SPENT VIA GIFT CARD" accentColor="text-emerald-400" />
          <AGMetricCard label="VAULT SECURITY" value="PIN ENCRYPTED" subtext="FIPS 140-2 VAULT" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Gift Card ID, Recipient..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['CARDS', 'BALANCES', 'ISSUANCE', 'TRANSACTIONS', 'SECURITY_VAULT', 'EXPIRATION', 'AUDIT'] as GiftCardsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'CARDS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">GIFT CARD ID</th>
                  <th className="p-3">CODE (MASKED)</th>
                  <th className="p-3">RECIPIENT</th>
                  <th className="p-3">INITIAL BALANCE</th>
                  <th className="p-3">CURRENT BALANCE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(g => (
                  <tr key={g.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{g.giftCardId}</td>
                    <td className="p-3 font-bold text-purple-400 font-mono">{g.codeMasked}</td>
                    <td className="p-3 font-bold text-slate-200">{g.recipient}</td>
                    <td className="p-3 text-slate-400">{g.initialBalance}</td>
                    <td className="p-3 font-bold text-emerald-400">{g.currentBalance} ({g.currency})</td>
                    <td className="p-3"><AGBadge status={g.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'CARDS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
