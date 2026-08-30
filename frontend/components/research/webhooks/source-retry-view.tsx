'use client';

import { WebhookRetrySchedule } from './source-types';

interface SourceRetryViewProps {
  retries: WebhookRetrySchedule[];
  onReplay: (ret: WebhookRetrySchedule) => void;
}

export function SourceRetryView({ retries, onReplay }: SourceRetryViewProps) {
  return (
    <div className="space-y-6 font-sans">
      <div className="bg-amber-50 p-4 rounded-2xl border border-amber-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div>
          <h3 className="font-bold text-amber-900">DEAD-LETTER &amp; RETRY QUEUE MANAGEMENT</h3>
          <p className="text-amber-700 mt-0.5">
            Failed webhooks enter exponential backoff retries. Exhausted events are moved to the Dead-Letter Queue for manual replay.
          </p>
        </div>
        <button
          onClick={() => alert('Batch replay executed for queued dead-letter events.')}
          className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl shadow-sm text-xs font-mono transition-colors"
        >
          REPLAY ALL EXHAUSTED (1)
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-mono text-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-[10px] text-slate-500 uppercase tracking-wider">
                <th className="px-4 py-3 font-semibold">RETRY ID</th>
                <th className="px-4 py-3 font-semibold">DELIVERY ID</th>
                <th className="px-4 py-3 font-semibold">EVENT TYPE</th>
                <th className="px-4 py-3 font-semibold">TARGET ENDPOINT</th>
                <th className="px-4 py-3 font-semibold">ATTEMPTS</th>
                <th className="px-4 py-3 font-semibold">SCHEDULED / STATUS</th>
                <th className="px-4 py-3 font-semibold">LAST ERROR</th>
                <th className="px-4 py-3 font-semibold text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {retries.map((ret) => (
                <tr key={ret.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3.5 font-bold text-slate-800">
                    {ret.retryId}
                  </td>
                  <td className="px-4 py-3.5 text-blue-600">
                    {ret.deliveryId}
                  </td>
                  <td className="px-4 py-3.5 font-bold text-purple-700">
                    {ret.eventType}
                  </td>
                  <td className="px-4 py-3.5 text-slate-700 font-sans">
                    <div className="font-bold">{ret.endpointName}</div>
                    <div className="text-[10px] text-slate-400 font-mono truncate max-w-[200px]">{ret.targetUrl}</div>
                  </td>
                  <td className="px-4 py-3.5 font-bold text-slate-800">
                    {ret.attemptCount} / {ret.maxAttempts}
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`px-2 py-0.5 rounded font-bold text-[10px] border ${
                      ret.status === 'EXHAUSTED' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-amber-50 text-amber-700 border-amber-200'
                    }`}>
                      {ret.scheduledAt}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-rose-600 text-[11px]">
                    {ret.lastError}
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <button
                      onClick={() => onReplay(ret)}
                      className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg text-[10px] transition-all"
                    >
                      MANUAL REPLAY
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
