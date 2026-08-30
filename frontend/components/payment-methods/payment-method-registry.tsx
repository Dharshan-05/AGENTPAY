'use client';

import { PaymentInstrumentRecord } from './payment-method-types';
import { AGBadge } from '@/components/ui/ag-badge';

interface PaymentMethodRegistryProps {
  instruments: PaymentInstrumentRecord[];
  onSelect: (item: PaymentInstrumentRecord) => void;
}

export function PaymentMethodRegistry({ instruments, onSelect }: PaymentMethodRegistryProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
            <th className="px-4 py-3 font-semibold">PM ID</th>
            <th className="px-4 py-3 font-semibold">METHOD</th>
            <th className="px-4 py-3 font-semibold">MASKED IDENTIFIER</th>
            <th className="px-4 py-3 font-semibold">OWNER / AGENT</th>
            <th className="px-4 py-3 font-semibold">STATUS</th>
            <th className="px-4 py-3 font-semibold">PROCESSOR</th>
            <th className="px-4 py-3 font-semibold">RISK</th>
            <th className="px-4 py-3 font-semibold">ENVIRONMENT</th>
            <th className="px-4 py-3 font-semibold">COUNTRY</th>
            <th className="px-4 py-3 font-semibold">CURRENCY</th>
            <th className="px-4 py-3 font-semibold">LAST USED</th>
            <th className="px-4 py-3 font-semibold text-right">ACTION</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.04] text-xs">
          {instruments.map((inst) => (
            <tr
              key={inst.id}
              onClick={() => onSelect(inst)}
              className="hover:bg-slate-900/40 transition-colors cursor-pointer group"
            >
              <td className="px-4 py-3.5 font-bold text-blue-400 group-hover:text-blue-300">
                {inst.instrumentId}
              </td>
              <td className="px-4 py-3.5 font-bold text-purple-400 text-[10px]">
                {inst.type}
              </td>
              <td className="px-4 py-3.5">
                <div className="font-bold text-slate-200">{inst.name}</div>
                <div className="text-[10px] text-slate-400">{inst.maskedIdentifier}</div>
              </td>
              <td className="px-4 py-3.5 text-slate-300">
                <div className="font-bold text-blue-400">{inst.agentId}</div>
                <div className="text-[10px] text-slate-500">{inst.agentName}</div>
              </td>
              <td className="px-4 py-3.5">
                <AGBadge status={inst.status} size="sm" />
              </td>
              <td className="px-4 py-3.5 font-bold text-slate-300">
                {inst.processor}
              </td>
              <td className="px-4 py-3.5 font-bold">
                <span className={
                  inst.riskTier === 'LOW' ? 'text-emerald-400' :
                  inst.riskTier === 'MEDIUM' ? 'text-amber-400' :
                  'text-red-400'
                }>
                  {inst.riskScore}/100 ({inst.riskTier})
                </span>
              </td>
              <td className="px-4 py-3.5">
                <AGBadge status={inst.environment} size="sm" />
              </td>
              <td className="px-4 py-3.5 text-slate-300">
                {inst.country}
              </td>
              <td className="px-4 py-3.5 text-slate-300">
                {inst.currency}
              </td>
              <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                {inst.lastUsedAt}
              </td>
              <td className="px-4 py-3.5 text-right">
                <button className="px-2.5 py-1 rounded bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 text-[10px] font-bold transition-all">
                  INSPECT
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
