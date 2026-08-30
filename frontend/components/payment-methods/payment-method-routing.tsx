'use client';

import { RoutingDecisionRecord } from './payment-method-types';

interface PaymentMethodRoutingProps {
  decisions: RoutingDecisionRecord[];
}

export function PaymentMethodRouting({ decisions }: PaymentMethodRoutingProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs overflow-x-auto space-y-4">
      <div className="text-xs font-bold text-slate-200 uppercase tracking-wider">
        SMART PAYMENT METHOD ROUTING &amp; FALLBACK ENGINE
      </div>

      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
            <th className="px-4 py-3 font-semibold">PM ID &amp; NAME</th>
            <th className="px-4 py-3 font-semibold">ORIGIN AGENT</th>
            <th className="px-4 py-3 font-semibold">GEO / CURRENCY</th>
            <th className="px-4 py-3 font-semibold">OPTIMAL PROCESSOR</th>
            <th className="px-4 py-3 font-semibold">FALLBACK PROCESSOR</th>
            <th className="px-4 py-3 font-semibold">DECISION STATUS</th>
            <th className="px-4 py-3 font-semibold">LATENCY</th>
            <th className="px-4 py-3 font-semibold">DECISION REASON</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.04] text-xs">
          {decisions.map((dec) => (
            <tr key={dec.id} className="hover:bg-slate-900/40 transition-colors">
              <td className="px-4 py-3.5">
                <div className="font-bold text-blue-400">{dec.methodId}</div>
                <div className="text-[10px] text-slate-400">{dec.methodName}</div>
              </td>
              <td className="px-4 py-3.5 font-bold text-slate-300">
                {dec.agentId}
              </td>
              <td className="px-4 py-3.5 text-slate-400 text-[10px]">
                {dec.requestedCountry} / {dec.requestedCurrency}
              </td>
              <td className="px-4 py-3.5 font-bold text-emerald-400">
                {dec.selectedProcessor}
              </td>
              <td className="px-4 py-3.5 text-slate-400">
                {dec.fallbackProcessor}
              </td>
              <td className="px-4 py-3.5 font-bold">
                <span className={
                  dec.status === 'OPTIMAL' ? 'text-emerald-400' :
                  dec.status === 'FALLBACK' ? 'text-amber-400' :
                  'text-red-400'
                }>
                  {dec.status}
                </span>
              </td>
              <td className="px-4 py-3.5 text-slate-300 font-bold">
                {dec.latencyMs}ms
              </td>
              <td className="px-4 py-3.5 text-slate-400 font-sans text-[11px]">
                {dec.decisionReason}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
