'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { DiscrepancyRecord } from './reconciliation-types';
import { AlertTriangle, Layers } from 'lucide-react';

interface DiscrepancyInspectorProps {
  discrepancy: DiscrepancyRecord | null;
  onClose: () => void;
}

export function DiscrepancyInspector({ discrepancy, onClose }: DiscrepancyInspectorProps) {
  if (!discrepancy) return null;

  return (
    <AGDrawer
      isOpen={!!discrepancy}
      onClose={onClose}
      title={`VARIANCE INSPECTOR: ${discrepancy.varianceId}`}
      subtitle="FINANCIAL COMPARISON & DELTA AUDIT"
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
            <span className="text-[10px] text-slate-400 block uppercase">VARIANCE DELTA</span>
            <span className="text-base font-bold text-red-400">{discrepancy.deltaAmount}</span>
          </div>
          <AGBadge status="REVIEW" label={`● ${discrepancy.severity} SEVERITY`} />
        </div>

        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Transaction ID:</span>
            <span className="text-slate-200 font-bold">{discrepancy.transactionId}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Agent Persona:</span>
            <span className="text-blue-400 font-bold">{discrepancy.agentId}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Processor:</span>
            <span className="text-slate-200 font-bold">{discrepancy.processor}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Expected Amount:</span>
            <span className="text-slate-200 font-bold">{discrepancy.expectedAmount}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Actual Settled:</span>
            <span className="text-emerald-400 font-bold">{discrepancy.actualAmount}</span>
          </div>
        </div>

        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
            RECOMMENDED ACTION
          </h4>
          <p className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] text-amber-400 leading-relaxed font-bold text-[11px]">
            {discrepancy.recommendation}
          </p>
        </div>
      </div>
    </AGDrawer>
  );
}
