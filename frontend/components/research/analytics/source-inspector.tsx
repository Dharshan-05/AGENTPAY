'use client';

import { SourceAgentRecord } from './source-types';
import { X, ShieldCheck, Copy, Activity } from 'lucide-react';

interface SourceInspectorProps {
  item: SourceAgentRecord | null;
  onClose: () => void;
}

export function SourceInspector({ item, onClose }: SourceInspectorProps) {
  if (!item) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex justify-end font-sans">
      <div className="w-full max-w-md bg-white h-full shadow-2xl p-6 flex flex-col justify-between overflow-y-auto space-y-6">
        
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div>
              <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold">SOURCE INSPECTOR</span>
              <h2 className="text-lg font-bold text-slate-900">{item.name}</h2>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Agent Persona ID:</span>
              <span className="font-mono font-bold text-slate-900">{item.agentId}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Transaction Volume:</span>
              <span className="font-mono font-bold text-slate-900">{item.transactions}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Success Rate:</span>
              <span className="font-mono font-bold text-emerald-600">{item.successRate}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Average Risk Score:</span>
              <span className="font-mono font-bold text-amber-600">{item.avgRisk}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Policy Interventions:</span>
              <span className="font-mono font-bold text-slate-700">{item.policyViolations}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Total Spend Value:</span>
              <span className="font-mono font-bold text-blue-600">{item.totalValue}</span>
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-900 uppercase">Excavated Component Pattern</h4>
            <p className="text-xs text-slate-500">
              Slide-over inspector drawer for detailed analytics drill-down. Source architecture: Tremor/shadcn Sheet primitive.
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 bg-slate-900 text-white text-xs font-bold rounded-xl hover:bg-slate-800 transition-colors"
        >
          Close Inspector
        </button>

      </div>
    </div>
  );
}
