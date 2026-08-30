'use client';

import { SourceAgentRecord } from './source-types';
import { X, ShieldCheck, Lock, Activity } from 'lucide-react';

interface SourceInspectorProps {
  agent: SourceAgentRecord | null;
  onClose: () => void;
}

export function SourceInspector({ agent, onClose }: SourceInspectorProps) {
  if (!agent) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex justify-end font-sans">
      <div className="w-full max-w-md bg-white h-full shadow-2xl p-6 flex flex-col justify-between overflow-y-auto space-y-6 text-slate-800">
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div>
              <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold">AGENT IDENTITY INSPECTOR</span>
              <h2 className="text-lg font-bold text-slate-900">{agent.name}</h2>
              <span className="font-mono text-xs font-bold text-blue-600">{agent.agentId}</span>
            </div>
            <button onClick={onClose} className="p-1 rounded hover:bg-slate-100 text-slate-400">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs font-mono">
            <div className="flex justify-between"><span className="text-slate-500">Execution Type:</span><span className="font-bold text-slate-900 font-sans">{agent.type}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Department Owner:</span><span className="font-bold text-slate-900 font-sans">{agent.owner}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Operating Env:</span><span className="font-bold text-slate-800">{agent.environment}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Risk Tier:</span><span className="font-bold text-emerald-600">{agent.riskTier}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Policy Binding:</span><span className="text-slate-700">{agent.policyBinding}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Health Score:</span><span className="font-bold text-emerald-600">{agent.healthScore}%</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Last Active:</span><span className="text-slate-600">{agent.lastActive}</span></div>
          </div>

          <div className="p-4 bg-blue-50 rounded-xl border border-blue-200 space-y-2 text-xs">
            <h4 className="font-bold text-blue-900 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-blue-600" /> Zero-Trust Security Health
            </h4>
            <p className="text-blue-800 text-[11px] leading-relaxed">
              mTLS Identity Certificate active. Next automated credential rotation due in <strong className="font-mono">{agent.credentialRotationDays} days</strong>.
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 bg-slate-900 text-white font-bold rounded-xl text-xs hover:bg-slate-800 transition-colors"
        >
          Close Inspector
        </button>
      </div>
    </div>
  );
}
