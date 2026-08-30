'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionAuditEventRecord } from './settings-types';
import { FileCode2, Copy, Check } from 'lucide-react';
import { useState } from 'react';

interface AuditInspectorProps {
  audit: ProductionAuditEventRecord | null;
  onClose: () => void;
}

export function AuditInspector({ audit, onClose }: AuditInspectorProps) {
  const [copiedHash, setCopiedHash] = useState(false);

  if (!audit) return null;

  const copyHash = () => {
    navigator.clipboard.writeText(audit.auditHash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  return (
    <AGDrawer
      isOpen={!!audit}
      onClose={onClose}
      title={`AUDIT EVENT INSPECTOR: ${audit.id}`}
      subtitle="IMMUTABLE SECURITY & SYSTEM AUDIT LEDGER ENTRY"
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
            <span className="text-[10px] text-slate-400 block uppercase">EVENT TYPE</span>
            <span className="text-base font-bold text-blue-400">{audit.event}</span>
          </div>
          <AGBadge status="APPROVED" label={`● ${audit.result}`} />
        </div>

        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Actor ID:</span>
            <span className="text-slate-200 font-bold">{audit.actor}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Target Resource:</span>
            <span className="text-emerald-400 font-bold">{audit.resource}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">IP Address:</span>
            <span className="text-blue-400 font-bold">{audit.ipAddress}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Timestamp:</span>
            <span className="text-slate-400">{audit.timestamp}</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950 border border-white/[0.04] space-y-1 text-[10px]">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Cryptographic Audit Hash:</span>
            <button onClick={copyHash} className="text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1">
              {copiedHash ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {copiedHash ? 'COPIED' : 'COPY'}
            </button>
          </div>
          <div className="text-emerald-400 font-mono text-[9px] break-all">{audit.auditHash}</div>
        </div>
      </div>
    </AGDrawer>
  );
}
