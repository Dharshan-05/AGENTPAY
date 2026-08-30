'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { SettlementBatchRecord } from './reconciliation-types';
import { Scale, Copy, Check, Layers } from 'lucide-react';
import { useState } from 'react';

interface SettlementInspectorProps {
  batch: SettlementBatchRecord | null;
  onClose: () => void;
}

export function SettlementInspector({ batch, onClose }: SettlementInspectorProps) {
  const [copiedHash, setCopiedHash] = useState(false);

  if (!batch) return null;

  const copyHash = () => {
    navigator.clipboard.writeText(batch.auditHash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  return (
    <AGDrawer
      isOpen={!!batch}
      onClose={onClose}
      title={`SETTLEMENT BATCH INSPECTOR: ${batch.id}`}
      subtitle="GATEWAY CLEARING & RECONCILIATION MATCHING PIPELINE"
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
            <span className="text-[10px] text-slate-400 block uppercase">PROCESSOR BATCH</span>
            <span className="text-base font-bold text-blue-400">{batch.processor}</span>
          </div>
          <AGBadge status="APPROVED" label={`● ${batch.status}`} />
        </div>

        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Gross Amount:</span>
            <span className="text-slate-200 font-bold">{batch.grossAmount}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Processing Fees:</span>
            <span className="text-red-400 font-bold">{batch.fees}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Net Settlement Deposit:</span>
            <span className="text-emerald-400 font-bold">{batch.netAmount}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Matched Intent Count:</span>
            <span className="text-emerald-400 font-bold">{batch.matchedCount} Txns</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Unmatched Variances:</span>
            <span className="text-red-400 font-bold">{batch.unmatchedCount} Variances</span>
          </div>
        </div>

        {/* PIPELINE */}
        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5 font-mono">
            <Layers className="w-3.5 h-3.5 text-emerald-400" /> RECONCILIATION PIPELINE STEPS
          </h4>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-3 text-[10px]">
            <div className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-[9px]">01</span>
              <div><span className="font-bold text-slate-200">Payment Intent Identified</span></div>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center justify-center font-bold text-[9px]">02</span>
              <div><span className="font-bold text-blue-400">Processor Record Imported</span></div>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30 flex items-center justify-center font-bold text-[9px]">03</span>
              <div><span className="font-bold text-purple-400">Transaction Matched</span></div>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-[9px]">04</span>
              <div><span className="font-bold text-emerald-400">Fee Calculation & Net Deposit Confirmed</span></div>
            </div>
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
          <div className="text-emerald-400 font-mono text-[9px] break-all">{batch.auditHash}</div>
        </div>
      </div>
    </AGDrawer>
  );
}
