'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { Search, RefreshCw } from 'lucide-react';
import { SearchTabType } from '@/components/transaction-search/transaction-search-types';
import { MOCK_SEARCH_RESULTS } from '@/components/transaction-search/transaction-search-data';

export default function TransactionSearchPage() {
  const [activeTab, setActiveTab] = useState<SearchTabType>('MULTI_SEARCH');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SEARCH_RESULTS.filter(s => 
      !search || s.searchId.toLowerCase().includes(search.toLowerCase()) || s.resultRef.toLowerCase().includes(search.toLowerCase()) || s.agentId.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="transaction-search">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="CROSS-DOMAIN TRANSACTION FORENSIC SEARCH"
          title="TRANSACTION"
          highlightTitle="SEARCH"
          description="Multi-axis forensic transaction search, processor reference correlation, agent identity lookup, and fraud investigation."
          icon={Search}
          statusBadge="● SEARCH INDEX HOT"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="SEARCH INDEX" value="1.4M Events" subtext="SUB-10MS LATENCY" accentColor="text-blue-400" />
          <AGMetricCard label="QUERIES 24H" value="48,920" subtext="INSPECTION LOOKUPS" accentColor="text-emerald-400" />
          <AGMetricCard label="INDEXED TXNS" value="823,910" subtext="CROSS-CONNECTOR" accentColor="text-purple-400" />
          <AGMetricCard label="FORENSIC MATCH" value="100%" subtext="EXACT RECONCILIATION" accentColor="text-emerald-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search TXN-ID, Agent, Customer, Processor Ref..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['MULTI_SEARCH', 'TRANSACTIONS', 'INTENTS', 'CUSTOMERS', 'AGENTS', 'PROCESSORS', 'FORENSICS', 'AUDIT'] as SearchTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'MULTI_SEARCH' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SEARCH ID</th>
                  <th className="p-3">QUERY TYPE</th>
                  <th className="p-3">RESULT REF</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">CUSTOMER</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3">TIMESTAMP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.searchId}</td>
                    <td className="p-3 font-bold text-purple-400">{s.queryType}</td>
                    <td className="p-3 font-bold text-slate-200">{s.resultRef}</td>
                    <td className="p-3 text-slate-300">{s.agentId}</td>
                    <td className="p-3 text-slate-300">{s.customer}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.amount}</td>
                    <td className="p-3 text-slate-400">{s.processor}</td>
                    <td className="p-3 text-slate-500">{s.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'MULTI_SEARCH' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
