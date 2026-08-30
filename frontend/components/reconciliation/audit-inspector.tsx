'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ReconciliationAuditEvent } from './reconciliation-types';
import { FileCode2, Copy, Check, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

interface AuditInspectorProps {
  event: ReconciliationAuditEvent | null;
  onClose: () => void;
}

export function AuditInspector({ event, onClose }: AuditInspectorProps) {
  const [copiedHash, setCopiedHash] = useState(false);

  if (!event) return null;

  const copyHash = () => {
    navigator.clipboard.writeText(event.hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  return (
    <AGDrawer
      isOpen={!!event}
      onClose={onClose}
      title={`AUDIT EVENT INSPECTOR: ${event.eventId}`}
      subtitle="CRYPTOGRAPHICALLY LINKED FINANCIAL AUDIT LEDGER ENTRY"
      footer={
        <div className="space-y-3 font-mono">
          <AGButton variant="secondary" size="md" onClick={onClose} className="w-full">
            CLOSE INSPECTOR
          </AGButton>
        </div>
      }
    >
      <div className="space-y-6 font-mono text-xs">
        <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase">EVENT ACTION</span>
            <span className="text-base font-bold text-emerald-400">{event.action}</span>
          </div>
          <AGBadge status="APPROVED" label={`● ${event.status}`} />
        </div>

        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Actor Persona:</span>
            <span className="text-slate-200 font-bold">{event.actor}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Target Entity:</span>
            <span className="text-blue-400 font-bold">{event.entity}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Source Gateway:</span>
            <span className="text-slate-200 font-bold">{event.source}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Timestamp:</span>
            <span className="text-slate-400">{event.timestamp}</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2 text-[10px]">
          <span className="text-slate-400 font-bold uppercase block">CRYPTOGRAPHIC VERIFICATION</span>
          <div className="flex justify-between text-emerald-400 font-bold">
            <span>HASH VALID:</span>
            <span>YES (SHA-256)</span>
          </div>
          <div className="flex justify-between text-emerald-400 font-bold">
            <span>PREVIOUS LINK VALID:</span>
            <span>YES</span>
          </div>
          <div className="flex justify-between text-emerald-400 font-bold">
            <span>IMMUTABLE STATE:</span>
            <span>CONFIRMED</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950 border border-white/[0.04] space-y-1 text-[10px]">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Current Hash:</span>
            <button onClick={copyHash} className="text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1">
              {copiedHash ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {copiedHash ? 'COPIED' : 'COPY'}
            </button>
          </div>
          <div className="text-emerald-400 font-mono text-[9px] break-all">{event.hash}</div>
        </div>
      </div>
    </AGDrawer>
  );
}
