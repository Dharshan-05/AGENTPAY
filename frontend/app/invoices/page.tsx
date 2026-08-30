'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { FileText, RefreshCw, Plus } from 'lucide-react';
import { InvoicesTabType } from '@/components/invoices/invoice-types';
import { MOCK_INVOICES } from '@/components/invoices/invoice-data';

export default function InvoicesPage() {
  const [activeTab, setActiveTab] = useState<InvoicesTabType>('REGISTRY');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_INVOICES.filter(i => 
      !search || i.invoiceId.toLowerCase().includes(search.toLowerCase()) || i.customer.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="invoices">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="ITEMIZED BILLING & INVOICE CONTROL PLANE"
          title="INVOICE"
          highlightTitle="OPERATIONS"
          description="Automated PDF invoice generation, line-item tax calculation, payment collection tracking, and credit note issuance."
          icon={FileText}
          statusBadge="● INVOICE ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Create Invoice Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> CREATE INVOICE</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TOTAL INVOICES" value={`${MOCK_INVOICES.length}`} subtext="ISSUED DOCUMENTS" accentColor="text-blue-400" />
          <AGMetricCard label="INVOICED VOLUME" value="$17,320.00" subtext="TOTAL INVOICED" accentColor="text-emerald-400" />
          <AGMetricCard label="PAID INVOICES" value="01" subtext="COLLECTED FUNDS" accentColor="text-emerald-400" />
          <AGMetricCard label="OPEN / PENDING" value="01" subtext="AWAITING PAYMENT" accentColor="text-amber-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Invoice ID, Customer..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'ISSUED', 'PAID', 'OVERDUE', 'CREDIT_NOTES', 'LINE_ITEMS', 'TAXES', 'AUDIT'] as InvoicesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'REGISTRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">INVOICE ID</th>
                  <th className="p-3">CUSTOMER</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">TAX</th>
                  <th className="p-3">DUE DATE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(i => (
                  <tr key={i.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{i.invoiceId}</td>
                    <td className="p-3 text-slate-200">{i.customer}</td>
                    <td className="p-3 font-bold text-purple-400">{i.agentId}</td>
                    <td className="p-3 font-bold text-slate-100">{i.amount}</td>
                    <td className="p-3 text-slate-400">{i.taxAmount}</td>
                    <td className="p-3 text-slate-400">{i.dueDate}</td>
                    <td className="p-3"><AGBadge status={i.status} size="sm" /></td>
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
