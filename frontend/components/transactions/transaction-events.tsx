'use client';

import { TxnEvent } from './transaction-types';

interface TransactionEventsProps {
  events: TxnEvent[];
}

export function TransactionEvents({ events }: TransactionEventsProps) {
  return (
    <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/60 font-mono text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">EVENT ID</th>
              <th className="px-4 py-3 font-semibold">EVENT TYPE</th>
              <th className="px-4 py-3 font-semibold">TRANSACTION ID</th>
              <th className="px-4 py-3 font-semibold">TIMESTAMP</th>
              <th className="px-4 py-3 font-semibold">ACTOR</th>
              <th className="px-4 py-3 font-semibold">LATENCY</th>
              <th className="px-4 py-3 font-semibold">STATUS</th>
              <th className="px-4 py-3 font-semibold">HTTP</th>
              <th className="px-4 py-3 font-semibold">AUDIT HASH</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04] font-mono text-xs">
            {events.map((ev) => {
              const isFailed = ev.status === 'FAILED' || (ev.responseCode && ev.responseCode >= 400);

              return (
                <tr key={ev.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-4 py-3.5 font-bold text-slate-300">
                    {ev.eventId}
                  </td>
                  <td className="px-4 py-3.5 font-bold text-blue-400">
                    {ev.eventType}
                  </td>
                  <td className="px-4 py-3.5 text-slate-400">
                    {ev.transactionId}
                  </td>
                  <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                    {ev.timestamp}
                  </td>
                  <td className="px-4 py-3.5 text-slate-200">
                    {ev.actor}
                  </td>
                  <td className="px-4 py-3.5 text-slate-400">
                    {ev.latencyMs}ms
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                      isFailed ? 'bg-red-500/10 text-red-400 border-red-500/30' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    }`}>
                      {ev.status}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 font-bold text-slate-300">
                    {ev.responseCode || 200}
                  </td>
                  <td className="px-4 py-3.5 text-[10px] text-slate-500 truncate max-w-[120px]">
                    {ev.auditHash}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
