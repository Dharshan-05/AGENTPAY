'use client';

import { ProcessorCapabilityRecord } from './source-types';

interface SourceProcessorMatrixProps {
  records: ProcessorCapabilityRecord[];
}

export function SourceProcessorMatrix({ records }: SourceProcessorMatrixProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs overflow-x-auto space-y-3">
      <div className="flex items-center justify-between text-[11px] text-slate-400">
        <span>MULTI-CONNECTOR PROCESSOR COMPATIBILITY MATRIX</span>
        <span className="text-[10px] text-slate-500">✓ Supported · ⚠️ Degraded · — Unsupported</span>
      </div>

      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
            <th className="px-4 py-3 font-semibold">METHOD TYPE</th>
            <th className="px-4 py-3 font-semibold text-center">STRIPE</th>
            <th className="px-4 py-3 font-semibold text-center">ADYEN</th>
            <th className="px-4 py-3 font-semibold text-center">JPMORGAN DIRECT</th>
            <th className="px-4 py-3 font-semibold text-center">CITIBANK DIRECT</th>
            <th className="px-4 py-3 font-semibold text-center">RAZORPAY</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.04] text-xs">
          {records.map((rec) => (
            <tr key={rec.methodType} className="hover:bg-slate-900/40 transition-colors">
              <td className="px-4 py-3.5 font-bold text-slate-200">
                {rec.methodType}
              </td>
              <td className="px-4 py-3.5 text-center font-bold">
                {rec.stripe === true ? <span className="text-emerald-400">✓ YES</span> : rec.stripe === 'DEGRADED' ? <span className="text-amber-400">⚠️ DEGRADED</span> : <span className="text-slate-600">—</span>}
              </td>
              <td className="px-4 py-3.5 text-center font-bold">
                {rec.adyen === true ? <span className="text-emerald-400">✓ YES</span> : rec.adyen === 'DEGRADED' ? <span className="text-amber-400">⚠️ DEGRADED</span> : <span className="text-slate-600">—</span>}
              </td>
              <td className="px-4 py-3.5 text-center font-bold">
                {rec.jpmorgan === true ? <span className="text-emerald-400">✓ YES</span> : rec.jpmorgan === 'DEGRADED' ? <span className="text-amber-400">⚠️ DEGRADED</span> : <span className="text-slate-600">—</span>}
              </td>
              <td className="px-4 py-3.5 text-center font-bold">
                {rec.citibank === true ? <span className="text-emerald-400">✓ YES</span> : rec.citibank === 'DEGRADED' ? <span className="text-amber-400">⚠️ DEGRADED</span> : <span className="text-slate-600">—</span>}
              </td>
              <td className="px-4 py-3.5 text-center font-bold">
                {rec.razorpay === true ? <span className="text-emerald-400">✓ YES</span> : rec.razorpay === 'DEGRADED' ? <span className="text-amber-400">⚠️ DEGRADED</span> : <span className="text-slate-600">—</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
