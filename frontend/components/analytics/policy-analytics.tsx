'use client';

import { AGCard } from '@/components/ui/ag-card';
import { PolicyTriggerRecord } from './analytics-types';
import { Shield, ExternalLink } from 'lucide-react';
import Link from 'next/link';

interface PolicyAnalyticsProps {
  policies: PolicyTriggerRecord[];
}

export function PolicyAnalytics({ policies }: PolicyAnalyticsProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-2 font-bold text-slate-100">
          <Shield className="w-4 h-4 text-emerald-400" />
          <span className="text-sm">AGENTGUARD POLICY INTELLIGENCE</span>
        </div>
        <Link href="/agentguard" className="text-[10px] text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1">
          AGENTGUARD <ExternalLink className="w-3 h-3" />
        </Link>
      </div>

      <div className="grid grid-cols-4 gap-2 text-[11px]">
        <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block">Evaluations</span>
          <span className="font-bold text-slate-100">18,492</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block">Passed</span>
          <span className="font-bold text-emerald-400">17,841</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block">Review</span>
          <span className="font-bold text-amber-400">482</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block">Blocked</span>
          <span className="font-bold text-red-400">169</span>
        </div>
      </div>

      <div className="space-y-2">
        <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
          TOP AGENTGUARD POLICY TRIGGERS
        </h4>

        <div className="p-3.5 rounded-xl bg-slate-950 border border-white/[0.04] space-y-2 text-[11px]">
          {policies.map((p) => (
            <div key={p.code} className="flex justify-between items-center p-2 rounded bg-slate-900/60 border border-white/[0.04]">
              <div>
                <span className="font-bold text-blue-400 mr-2">{p.code}</span>
                <span className="text-slate-200">{p.name}</span>
              </div>

              <div className="flex items-center gap-4 text-[10px]">
                <span className="text-slate-400">{p.evaluations.toLocaleString()} evals</span>
                <span className="text-amber-400 font-bold">{p.triggered} triggered</span>
                <span className="text-red-400 font-bold">{p.blockRate} block rate</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AGCard>
  );
}
