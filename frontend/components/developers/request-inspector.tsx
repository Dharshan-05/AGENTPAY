'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { DeveloperRequestLog } from './developers-types';
import { FileCode2, Copy, Check, ShieldCheck, Layers } from 'lucide-react';
import { useState } from 'react';

interface RequestInspectorProps {
  log: DeveloperRequestLog | null;
  onClose: () => void;
}

export function RequestInspector({ log, onClose }: RequestInspectorProps) {
  const [copiedHash, setCopiedHash] = useState(false);

  if (!log) return null;

  const copyTxnHash = () => {
    navigator.clipboard.writeText(log.txnHash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  return (
    <AGDrawer
      isOpen={!!log}
      onClose={onClose}
      title={`REQUEST INSPECTOR: ${log.requestId}`}
      subtitle="REAL-TIME HTTP AUDIT & PIPELINE TELEMETRY"
      footer={
        <div className="space-y-3 font-mono">
          <AGButton variant="secondary" size="md" onClick={onClose} className="w-full">
            CLOSE INSPECTOR
          </AGButton>
          <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-white/[0.08]">
            <span>Audit Hash Verified</span>
            <span>mTLS Connection Encrypted</span>
          </div>
        </div>
      }
    >
      <div className="space-y-6 font-mono text-xs">
        
        <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase">HTTP RESPONSE</span>
            <span className="text-base font-bold text-emerald-400">{log.statusCode} OK ({log.latency})</span>
          </div>
          <AGBadge status="APPROVED" label={`● ${log.method}`} />
        </div>

        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Endpoint Route:</span>
            <span className="text-slate-200 font-bold">{log.endpoint}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Agent Persona:</span>
            <span className="text-blue-400 font-bold">{log.agentId}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">AGENTGUARD Status:</span>
            <span className="text-emerald-400 font-bold">{log.agentGuardStatus} ({log.policyId})</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">FRAUDGUARD Vector:</span>
            <span className="text-amber-400 font-bold">Score {log.riskScore} ({log.fraudGuardStatus})</span>
          </div>
        </div>

        {/* SECURITY PIPELINE */}
        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5 font-mono">
            <Layers className="w-3.5 h-3.5 text-emerald-400" />
            ZERO-TRUST SECURITY PIPELINE STEPS
          </h4>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-3 text-[10px]">
            <div className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-[9px]">01</span>
              <div><span className="font-bold text-slate-200">Identity Authenticated</span> <span className="text-slate-500">(mTLS Verified)</span></div>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center justify-center font-bold text-[9px]">02</span>
              <div><span className="font-bold text-blue-400">API Credential Validated</span> <span className="text-slate-500">(Scope: payments:write)</span></div>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30 flex items-center justify-center font-bold text-[9px]">03</span>
              <div><span className="font-bold text-purple-400">AGENTGUARD Policy Evaluated</span> <span className="text-slate-500">({log.policyId})</span></div>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center font-bold text-[9px]">04</span>
              <div><span className="font-bold text-amber-400">FRAUDGUARD Risk Scored</span> <span className="text-slate-500">(Score: {log.riskScore})</span></div>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-[9px]">05</span>
              <div><span className="font-bold text-emerald-400">Request Authorized</span> <span className="text-slate-500">(200 OK)</span></div>
            </div>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950 border border-white/[0.04] space-y-1 text-[10px]">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Audit Ledger Hash:</span>
            <button onClick={copyTxnHash} className="text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1">
              {copiedHash ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {copiedHash ? 'COPIED' : 'COPY'}
            </button>
          </div>
          <div className="text-emerald-400 font-mono text-[9px] break-all">{log.txnHash}</div>
        </div>

      </div>
    </AGDrawer>
  );
}
