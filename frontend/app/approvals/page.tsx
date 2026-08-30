'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { ShieldCheck, RefreshCw, Download, CheckCircle, XCircle, ArrowRight } from 'lucide-react';
import { ApprovalsTabType, ApprovalRecord } from '@/components/approvals/approval-types';
import { MOCK_APPROVALS } from '@/components/approvals/approval-data';

export default function ApprovalsPage() {
  const [activeTab, setActiveTab] = useState<ApprovalsTabType>('QUEUE');
  const [search, setSearch] = useState('');
  const [selectedApr, setSelectedApr] = useState<ApprovalRecord | null>(null);

  const filtered = useMemo(() => {
    return MOCK_APPROVALS.filter(a => 
      !search || a.approvalId.toLowerCase().includes(search.toLowerCase()) || a.transactionId.toLowerCase().includes(search.toLowerCase()) || a.agentId.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="approvals">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="HUMAN-IN-THE-LOOP (HITL) GOVERNANCE QUEUE"
          title="HUMAN"
          highlightTitle="APPROVALS"
          description="Real-time HITL queue for high-value autonomous agent payment approvals, policy override governance, and SLA tracking."
          icon={ShieldCheck}
          statusBadge="● HITL QUEUE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="secondary" size="sm" onClick={() => alert('Exporting ledger...')}>EXPORT LEDGER</AGButton>
            </div>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <AGMetricCard label="PENDING APPROVALS" value="01" subtext="QUEUE SLA 15M" accentColor="text-amber-400" />
          <AGMetricCard label="APPROVED 24H" value="14" subtext="HUMAN AUTHORIZED" accentColor="text-emerald-400" />
          <AGMetricCard label="REJECTED 24H" value="03" subtext="POLICY DENIALS" accentColor="text-rose-400" />
          <AGMetricCard label="AVG RESPONSE SLA" value="4.2m" subtext="TARGET < 15M" accentColor="text-blue-400" />
          <AGMetricCard label="POLICY OVERRIDES" value="00" subtext="ZERO COMPLIANCE VIOLATIONS" accentColor="text-emerald-400" />
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search Approval ID, Transaction, Agent, Policy..."
            className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none"
          />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400 hover:text-slate-200">RESET</button>
        </div>

        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['QUEUE', 'PENDING', 'APPROVED', 'REJECTED', 'ESCALATED', 'POLICIES', 'SLA', 'AUDIT'] as ApprovalsTabType[]).map(t => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {t}
            </button>
          ))}
        </div>

        {activeTab === 'QUEUE' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-slate-950">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">APPROVAL ID</th>
                  <th className="p-3">TXN ID</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">POLICY ID</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">RISK SCORE</th>
                  <th className="p-3">SLA REMAINING</th>
                  <th className="p-3">STATUS</th>
                  <th className="p-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(a => (
                  <tr key={a.id} onClick={() => setSelectedApr(a)} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-amber-400">{a.approvalId}</td>
                    <td className="p-3 font-bold text-blue-400">{a.transactionId}</td>
                    <td className="p-3 font-bold text-purple-400">{a.agentId}</td>
                    <td className="p-3 text-slate-300">{a.policyId}</td>
                    <td className="p-3 font-bold text-slate-100">{a.amount}</td>
                    <td className="p-3 font-bold text-rose-400">{a.riskScore}/100</td>
                    <td className="p-3 text-amber-400 font-bold">{a.slaRemaining}</td>
                    <td className="p-3"><AGBadge status={a.status} size="sm" /></td>
                    <td className="p-3 text-right flex gap-1 justify-end">
                      <button onClick={(e) => { e.stopPropagation(); alert(`Approved ${a.approvalId}`); }} className="px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">APPROVE</button>
                      <button onClick={(e) => { e.stopPropagation(); alert(`Rejected ${a.approvalId}`); }} className="px-2 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px] font-bold">REJECT</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab !== 'QUEUE' && (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">
            {activeTab} OPERATIONAL VIEW ACTIVE — 2 HUMAN APPROVAL DECISIONS MONITORED
          </div>
        )}

        {selectedApr && (
          <AGDrawer isOpen={!!selectedApr} onClose={() => setSelectedApr(null)} title={`APPROVAL INSPECTOR: ${selectedApr.approvalId}`} subtitle="HUMAN-IN-THE-LOOP DECISION">
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-1">
                <div className="text-[9px] text-amber-400 font-bold uppercase">HITL CAUSAL TRACE</div>
                <div className="flex items-center gap-1 text-[10px]">
                  <span className="text-blue-400 font-bold">{selectedApr.agentId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-purple-400 font-bold">{selectedApr.policyId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-amber-400 font-bold">{selectedApr.approvalId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-emerald-400 font-bold">{selectedApr.status}</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1">
                <div className="flex justify-between"><span className="text-slate-500">Amount:</span><span className="text-slate-100 font-bold">{selectedApr.amount}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Risk Score:</span><span className="text-rose-400 font-bold">{selectedApr.riskScore}/100</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Requester:</span><span className="text-slate-300">{selectedApr.requester}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Approver:</span><span className="text-emerald-400 font-bold">{selectedApr.approver}</span></div>
              </div>
            </div>
          </AGDrawer>
        )}
      </div>
    </AgentPayShell>
  );
}
