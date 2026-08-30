'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { DeveloperApiKey } from './developers-types';
import { ApiKeyStatusBadge } from './api-key-status';
import { ShieldCheck, Copy, Check, Lock, RotateCcw, AlertOctagon } from 'lucide-react';
import { useState } from 'react';

interface ApiKeyInspectorProps {
  apiKey: DeveloperApiKey | null;
  onClose: () => void;
  onRevoke: (id: string) => void;
}

export function ApiKeyInspector({ apiKey, onClose, onRevoke }: ApiKeyInspectorProps) {
  const [copiedPrefix, setCopiedPrefix] = useState(false);

  if (!apiKey) return null;

  const copyPrefix = () => {
    navigator.clipboard.writeText(apiKey.keyPrefix);
    setCopiedPrefix(true);
    setTimeout(() => setCopiedPrefix(false), 2000);
  };

  return (
    <AGDrawer
      isOpen={!!apiKey}
      onClose={onClose}
      title={`API KEY INSPECTOR: ${apiKey.name}`}
      subtitle="ZERO-TRUST CREDENTIAL GOVERNANCE & SECURITY SCOPE"
      footer={
        <div className="space-y-3 font-mono">
          <div className="grid grid-cols-2 gap-2">
            {apiKey.status === 'ACTIVE' && (
              <AGButton variant="danger" size="md" onClick={() => onRevoke(apiKey.id)}>
                REVOKE KEY
              </AGButton>
            )}
            <AGButton variant="secondary" size="md" onClick={onClose}>
              CLOSE INSPECTOR
            </AGButton>
          </div>
          <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-white/[0.08]">
            <span>Key ID: {apiKey.id}</span>
            <span>mTLS Authentication Enforced</span>
          </div>
        </div>
      }
    >
      <div className="space-y-6 font-mono text-xs">
        
        {/* VERDICT BANNER */}
        <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase">CREDENTIAL STATUS</span>
            <span className="text-base font-bold text-slate-100">{apiKey.status}</span>
          </div>
          <ApiKeyStatusBadge status={apiKey.status} />
        </div>

        {/* SECURITY POSTURE SUMMARY */}
        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-blue-400 font-bold flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4" /> AGENT SECURITY BOUNDS
            </span>
            <span className="text-emerald-400 font-bold">ZERO-TRUST VERIFIED</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[10px]">
            <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
              <span className="text-slate-400 block">Agent Persona</span>
              <span className="font-bold text-slate-200">{apiKey.agentId}</span>
            </div>
            <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
              <span className="text-slate-400 block">Governance Policy</span>
              <span className="font-bold text-blue-400">{apiKey.policyId}</span>
            </div>
            <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
              <span className="text-slate-400 block">FRAUDGUARD Vector</span>
              <span className="font-bold text-emerald-400">{apiKey.fraudGuardStatus}</span>
            </div>
            <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
              <span className="text-slate-400 block">IP Restriction</span>
              <span className="font-bold text-emerald-400">{apiKey.ipRestriction ? 'ENABLED' : 'DISABLED'}</span>
            </div>
          </div>
        </div>

        {/* TOKEN PREFIX */}
        <div className="p-3.5 rounded-xl bg-slate-950 border border-white/[0.04] space-y-1 text-[10px]">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Token Prefix:</span>
            <button onClick={copyPrefix} className="text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1">
              {copiedPrefix ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {copiedPrefix ? 'COPIED' : 'COPY'}
            </button>
          </div>
          <div className="text-emerald-400 font-mono text-[11px] font-bold">{apiKey.keyPrefix}••••••••••••</div>
        </div>

        {/* SCOPES */}
        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
            GRANTED OAUTH SCOPES
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {apiKey.scopes.map((s) => (
              <span key={s} className="px-2.5 py-1 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/30 text-[10px] font-bold">
                {s}
              </span>
            ))}
          </div>
        </div>

        {/* TIMESTAMPS */}
        <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Created Date:</span>
            <span className="text-slate-200">{apiKey.created}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Last Active Usage:</span>
            <span className="text-slate-200">{apiKey.lastUsed}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Current Request Rate:</span>
            <span className="text-blue-400 font-bold">{apiKey.requestRate}</span>
          </div>
        </div>

      </div>
    </AGDrawer>
  );
}
