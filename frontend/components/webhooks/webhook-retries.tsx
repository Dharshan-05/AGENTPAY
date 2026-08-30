'use client';

import { WebhookRetrySchedule } from './webhook-types';
import { AGBadge } from '@/components/ui/ag-badge';

interface WebhookRetriesProps {
  retries: WebhookRetrySchedule[];
  onReplay: (retry: WebhookRetrySchedule) => void;
}

export function WebhookRetries({ retries, onReplay }: WebhookRetriesProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
            <th className="px-4 py-3 font-semibold">RETRY ID</th>
            <th className="px-4 py-3 font-semibold">DELIVERY / EVENT</th>
            <th className="px-4 py-3 font-semibold">TARGET ENDPOINT</th>
            <th className="px-4 py-3 font-semibold">ATTEMPTS</th>
            <th className="px-4 py-3 font-semibold">SCHEDULED BACKOFF</th>
            <th className="px-4 py-3 font-semibold">LAST ERROR</th>
            <th className="px-4 py-3 font-semibold">STATUS</th>
            <th className="px-4 py-3 font-semibold text-right">ACTION</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.04] text-xs">
          {retries.map((ret) => (
            <tr key={ret.id} className="hover:bg-slate-900/40 transition-colors">
              <td className="px-4 py-3.5 font-bold text-amber-400">
                {ret.retryId}
              </td>
              <td className="px-4 py-3.5 text-slate-300">
                <div className="font-bold text-blue-400">{ret.deliveryId}</div>
                <div className="text-[10px] text-slate-500">{ret.eventType}</div>
              </td>
              <td className="px-4 py-3.5 text-slate-300">
                {ret.endpointName}
              </td>
              <td className="px-4 py-3.5 text-slate-400 font-bold">
                {ret.attemptCount} / {ret.maxAttempts}
              </td>
              <td className="px-4 py-3.5 text-slate-300">
                {ret.scheduledAt}
              </td>
              <td className="px-4 py-3.5 text-red-400 text-[11px]">
                {ret.lastError}
              </td>
              <td className="px-4 py-3.5">
                <AGBadge status={ret.status} size="sm" />
              </td>
              <td className="px-4 py-3.5 text-right">
                <button
                  onClick={() => onReplay(ret)}
                  className="px-2.5 py-1 rounded bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold transition-all"
                >
                  REPLAY NOW
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
