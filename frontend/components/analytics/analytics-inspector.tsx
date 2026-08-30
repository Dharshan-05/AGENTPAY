'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { AgentPerformanceRecord, AnomalyRecord } from './analytics-types';
import { ShieldCheck, Cpu, Layers, Copy, Check, BarChart3, Lock } from 'lucide-react';
import { useState } from 'react';

interface AnalyticsInspectorProps {
  agentItem: AgentPerformanceRecord | null;
  anomalyItem: AnomalyRecord | null;
  onClose: () => void;
}

export function AnalyticsInspector({ agentItem, anomalyItem, onClose }: AnalyticsInspectorProps) {
  const [copiedHash, setCopiedHash] = useState(false);

  const title = agentItem
    ? `ANALYTICS INSPECTOR: ${agentItem.agentName}`
    : anomalyItem
    ? `ANOMALY INSPECTOR: ${anomalyItem.anomaly}`
    : 'ANALYTICS INSPECTOR';

  const subtitle = agentItem
    ? `AGENT PERSONA (${agentItem.agentId}) PERFORMANCE TELEMETRY`
    : anomalyItem
    ? `BEHAVIORAL DEVIATION & ANOMALY DETECTED`
    : 'DETAILED INTELLIGENCE DRILL-DOWN';

  const copyLedgerHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  if (!agentItem && !anomalyItem) return null;

  return (
    <AGDrawer
      isOpen={!!agentItem || !!anomalyItem}
      onClose={onClose}
      title={title}
      subtitle={subtitle}
      footer={
        <div className="space-y-3 font-mono">
          <div className="grid grid-cols-2 gap-2">
            <AGButton variant="primary" size="md" onClick={onClose}>
              EXPORT DRILL-DOWN
            </AGButton>
            <AGButton variant="secondary" size="md" onClick={onClose}>
              CLOSE INSPECTOR
            </AGButton>
          </div>
          <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-white/[0.08]">
            <span>Telemetry Session: active-session-99182</span>
            <span>Cryptographically Verified</span>
          </div>
        </div>
      }
    >
      <div className="space-y-6 font-mono text-xs">
        
        {/* AGENT DRILL-DOWN */}
        {agentItem && (
          <>
            <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-400 block uppercase">PERFORMANCE STATUS</span>
                <span className="text-base font-bold text-slate-100">{agentItem.decision}</span>
              </div>
              <AGBadge
                status={agentItem.decision === 'AUTHORIZED' ? 'APPROVED' : agentItem.decision === 'BLOCKED' ? 'BLOCKED' : 'REVIEW'}
                label={`● ${agentItem.decision}`}
              />
            </div>

            <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-blue-400 font-bold flex items-center gap-1.5">
                  <BarChart3 className="w-4 h-4" /> AGENT METRICS SUMMARY
                </span>
                <span className="text-emerald-400 font-bold">{agentItem.successRate} Success</span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
                  <span className="text-slate-400 block">Total Transactions</span>
                  <span className="font-bold text-slate-200">{agentItem.transactions}</span>
                </div>
                <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
                  <span className="text-slate-400 block">Average Risk Score</span>
                  <span className="font-bold text-amber-400">{agentItem.avgRisk} / 100</span>
                </div>
                <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
                  <span className="text-slate-400 block">Policy Interventions</span>
                  <span className="font-bold text-red-400">{agentItem.policyViolations}</span>
                </div>
                <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
                  <span className="text-slate-400 block">Total Spend Volume</span>
                  <span className="font-bold text-emerald-400">{agentItem.totalValue}</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                CROSS-MODULE SECURITY CONNECTIONS
              </h4>
              <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-slate-400">AGENTGUARD Policy:</span>
                  <span className="text-blue-400 font-bold">AGP-GOV-001 (Spend Governance)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">FRAUDGUARD Vector:</span>
                  <span className="text-emerald-400 font-bold">Low Risk (Score {agentItem.avgRisk})</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Payment Engine Rail:</span>
                  <span className="text-slate-200 font-semibold">Visa / Mastercard Tokenized Virtual Card</span>
                </div>
              </div>
            </div>
          </>
        )}

        {/* ANOMALY DRILL-DOWN */}
        {anomalyItem && (
          <>
            <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-400 block uppercase">SEVERITY LEVEL</span>
                <span className="text-base font-bold text-red-400">{anomalyItem.severity}</span>
              </div>
              <AGBadge status="BLOCKED" label={`● ${anomalyItem.status}`} />
            </div>

            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 space-y-2 text-[11px]">
              <div className="flex justify-between">
                <span className="text-slate-400">Agent Persona:</span>
                <span className="text-slate-200 font-bold">{anomalyItem.agent} ({anomalyItem.agentId})</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Risk Score Peak:</span>
                <span className="text-red-400 font-bold">{anomalyItem.riskScore} / 100</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Detected Timestamp:</span>
                <span className="text-slate-400">{anomalyItem.detectedAt}</span>
              </div>
            </div>
          </>
        )}

        {/* CRYPTOGRAPHIC TRANSACTION AUDIT HASH */}
        <div className="p-3.5 rounded-xl bg-slate-950 border border-white/[0.04] space-y-1 text-[10px]">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Ledger Audit Hash:</span>
            <button
              onClick={() => copyLedgerHash('0x9F4AC8102E3B881900281F7A9B8411')}
              className="text-blue-400 hover:text-blue-300 flex items-center gap-1 font-bold"
            >
              {copiedHash ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {copiedHash ? 'COPIED' : 'COPY'}
            </button>
          </div>
          <div className="text-emerald-400 font-mono text-[9px] break-all">
            0x9F4AC8102E3B881900281F7A9B8411
          </div>
        </div>

      </div>
    </AGDrawer>
  );
}
