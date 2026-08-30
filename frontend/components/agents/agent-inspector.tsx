'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionAgentRecord } from './agent-types';
import { ShieldCheck, Lock, Activity, Bot } from 'lucide-react';

interface AgentInspectorProps {
  agent: ProductionAgentRecord | null;
  onClose: () => void;
}

export function AgentInspector({ agent, onClose }: AgentInspectorProps) {
  if (!agent) return null;

  return (
    <AGDrawer
      isOpen={!!agent}
      onClose={onClose}
      title={`AGENT IDENTITY INSPECTOR: ${agent.agentId}`}
      subtitle="ZERO-TRUST IDENTITY & AGENT OPERATIONS CONTROL"
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
            <span className="text-[10px] text-slate-400 block uppercase">AGENT PERSONA</span>
            <span className="text-base font-bold text-slate-100">{agent.name}</span>
          </div>
          <AGBadge status="APPROVED" label={`● ${agent.status}`} />
        </div>

        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Agent ID:</span>
            <span className="text-blue-400 font-bold">{agent.agentId}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Execution Type:</span>
            <span className="text-slate-200 font-bold">{agent.type}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Department Owner:</span>
            <span className="text-slate-200 font-bold">{agent.owner}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Environment:</span>
            <span className="text-slate-200 font-bold">{agent.environment}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Risk Tier:</span>
            <span className="text-emerald-400 font-bold">{agent.riskTier}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Policy Binding:</span>
            <span className="text-slate-300 font-mono text-[10px]">{agent.policyBinding}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Health Score:</span>
            <span className="text-emerald-400 font-bold">{agent.healthScore}%</span>
          </div>
        </div>

        {/* SECURITY POSTURE */}
        <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2 text-[10px]">
          <h4 className="font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> ZERO-TRUST SECURITY HEALTH
          </h4>
          <div className="flex justify-between text-emerald-400 font-bold">
            <span>mTLS CERTIFICATE:</span>
            <span>VALID</span>
          </div>
          <div className="flex justify-between text-slate-300">
            <span>CREDENTIAL ROTATION:</span>
            <span className="text-purple-400 font-bold">DUE IN {agent.credentialRotationDays} DAYS</span>
          </div>
        </div>
      </div>
    </AGDrawer>
  );
}
