'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { DisputeRecord } from './reconciliation-types';
import { ShieldAlert, FileText, CheckCircle2, Clock } from 'lucide-react';

interface DisputeInspectorProps {
  dispute: DisputeRecord | null;
  onClose: () => void;
}

export function DisputeInspector({ dispute, onClose }: DisputeInspectorProps) {
  if (!dispute) return null;

  return (
    <AGDrawer
      isOpen={!!dispute}
      onClose={onClose}
      title={`DISPUTE DOSSIER: ${dispute.disputeId}`}
      subtitle="CHARGEBACK ARBITRATION & EVIDENCE SUBMISSION"
      footer={
        <div className="space-y-3 font-mono">
          <AGButton variant="secondary" size="md" onClick={onClose} className="w-full">
            CLOSE DOSSIER
          </AGButton>
        </div>
      }
    >
      <div className="space-y-6 font-mono text-xs">
        <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase">DISPUTE AMOUNT</span>
            <span className="text-base font-bold text-red-400">{dispute.amount}</span>
          </div>
          <AGBadge status="REVIEW" label={`● ${dispute.status}`} />
        </div>

        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Transaction ID:</span>
            <span className="text-slate-200 font-bold">{dispute.transactionId}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Agent Persona:</span>
            <span className="text-blue-400 font-bold">{dispute.agentId}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Merchant Target:</span>
            <span className="text-slate-200 font-bold">{dispute.merchant}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Reason Code:</span>
            <span className="text-slate-300 font-bold">{dispute.reason}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Evidence Deadline:</span>
            <span className="text-amber-400 font-bold">{dispute.deadline}</span>
          </div>
        </div>

        {/* EVIDENCE DOSSIER */}
        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5 font-mono">
            <FileText className="w-3.5 h-3.5 text-blue-400" /> EVIDENCE DOSSIER STATUS
          </h4>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2.5 text-[10px]">
            <div className="flex justify-between items-center">
              <span>Payment Authorization Intent:</span>
              <span className="text-emerald-400 font-bold">VERIFIED</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Agent mTLS Identity Certificate:</span>
              <span className="text-emerald-400 font-bold">VERIFIED</span>
            </div>
            <div className="flex justify-between items-center">
              <span>AGENTGUARD Policy Decision (AGP-GOV-001):</span>
              <span className="text-emerald-400 font-bold">VERIFIED</span>
            </div>
            <div className="flex justify-between items-center">
              <span>FRAUDGUARD Risk Vector Scorecard:</span>
              <span className="text-emerald-400 font-bold">VERIFIED</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Processor Response Payload:</span>
              <span className="text-blue-400 font-bold">AVAILABLE</span>
            </div>
          </div>
        </div>
      </div>
    </AGDrawer>
  );
}
