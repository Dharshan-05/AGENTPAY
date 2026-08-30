'use client';

import { MethodRiskRecord } from './source-types';
import { AlertTriangle } from 'lucide-react';

interface SourceRiskProps {
  records: MethodRiskRecord[];
}

export function SourceRisk({ records }: SourceRiskProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs overflow-x-auto space-y-4">
      <div className="flex items-center justify-between text-xs font-bold text-slate-200">
        <span className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" /> FRAUDGUARD METHOD-LEVEL RISK EVALUATION
        </span>
      </div>

      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
            <th className="px-4 py-3 font-semibold">INSTRUMENT</th>
            <th className="px-4 py-3 font-semibold">AGENT ID</th>
            <th className="px-4 py-3 font-semibold">RISK SCORE</th>
            <th className="px-4 py-3 font-semibold">RISK TIER</th>
            <th className="px-4 py-3 font-semibold">VELOCITY FLAG</th>
            <th className="px-4 py-3 font-semibold">GEO MISMATCH</th>
            <th className="px-4 py-3 font-semibold">BEHAVIOR RATING</th>
            <th className="px-4 py-3 font-semibold">POLICY RESTRICTION</th>
            <th className="px-4 py-3 font-semibold">HITL REQUIRED</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.04] text-xs">
          {records.map((rsk) => (
            <tr key={rsk.id} className="hover:bg-slate-900/40 transition-colors">
              <td className="px-4 py-3.5 font-bold text-slate-200">
                {rsk.instrumentName}
              </td>
              <td className="px-4 py-3.5 font-bold text-blue-400">
                {rsk.agentId}
              </td>
              <td className="px-4 py-3.5 font-bold text-lg">
                <span className={rsk.riskScore < 30 ? 'text-emerald-400' : rsk.riskScore < 70 ? 'text-amber-400' : 'text-red-400'}>
                  {rsk.riskScore} / 100
                </span>
              </td>
              <td className="px-4 py-3.5 font-bold">
                <span className={rsk.riskTier === 'LOW' ? 'text-emerald-400' : rsk.riskTier === 'MEDIUM' ? 'text-amber-400' : 'text-red-400'}>
                  {rsk.riskTier}
                </span>
              </td>
              <td className="px-4 py-3.5 font-bold">
                {rsk.velocityFlag ? <span className="text-red-400">FLAGGED</span> : <span className="text-emerald-400">CLEAR</span>}
              </td>
              <td className="px-4 py-3.5 font-bold">
                {rsk.geoMismatchFlag ? <span className="text-red-400">MISMATCH</span> : <span className="text-emerald-400">MATCH</span>}
              </td>
              <td className="px-4 py-3.5 font-bold text-slate-300">
                {rsk.agentBehaviorRating}
              </td>
              <td className="px-4 py-3.5 text-slate-400 font-sans text-[11px]">
                {rsk.policyRestriction}
              </td>
              <td className="px-4 py-3.5 font-bold">
                {rsk.hitlRequired ? <span className="text-amber-400">YES — APPROVAL REQUIRED</span> : <span className="text-emerald-400">NO</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
