'use client';

import { WebhookDeliveryRecord } from './source-types';

interface SourceDeliveryLogProps {
  deliveries: WebhookDeliveryRecord[];
  onSelect: (dlv: WebhookDeliveryRecord) => void;
}

export function SourceDeliveryLog({ deliveries, onSelect }: SourceDeliveryLogProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 font-mono text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">DELIVERY ID</th>
              <th className="px-4 py-3 font-semibold">EVENT TYPE</th>
              <th className="px-4 py-3 font-semibold">TARGET ENDPOINT</th>
              <th className="px-4 py-3 font-semibold">STATUS</th>
              <th className="px-4 py-3 font-semibold">HTTP</th>
              <th className="px-4 py-3 font-semibold">LATENCY</th>
              <th className="px-4 py-3 font-semibold">ATTEMPTS</th>
              <th className="px-4 py-3 font-semibold">TIMESTAMP</th>
              <th className="px-4 py-3 font-semibold text-right">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-mono text-xs">
            {deliveries.map((dlv) => {
              const isDelivered = dlv.status === 'DELIVERED';
              const isExhausted = dlv.status === 'EXHAUSTED';
              const isRetrying = dlv.status === 'RETRYING';

              return (
                <tr
                  key={dlv.id}
                  onClick={() => onSelect(dlv)}
                  className="hover:bg-slate-50 transition-colors cursor-pointer group"
                >
                  <td className="px-4 py-3.5 font-bold text-slate-800">
                    {dlv.deliveryId}
                  </td>
                  <td className="px-4 py-3.5 font-bold text-purple-700">
                    {dlv.eventType}
                  </td>
                  <td className="px-4 py-3.5 text-slate-700 font-sans">
                    <div className="font-bold">{dlv.endpointName}</div>
                    <div className="text-[10px] font-mono text-slate-400 truncate max-w-[200px]">{dlv.targetUrl}</div>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                      isDelivered ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      isExhausted ? 'bg-rose-50 text-rose-700 border-rose-200' :
                      isRetrying ? 'bg-amber-50 text-amber-700 border-amber-200' :
                      'bg-slate-100 text-slate-600 border-slate-200'
                    }`}>
                      {dlv.status}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 font-bold">
                    <span className={dlv.responseStatus === 200 ? 'text-emerald-600' : 'text-rose-600'}>
                      {dlv.responseStatus}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-slate-600">
                    {dlv.latencyMs}ms
                  </td>
                  <td className="px-4 py-3.5 text-slate-700 font-bold">
                    {dlv.attemptCount} / {dlv.maxRetries}
                  </td>
                  <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                    {dlv.createdTimestamp}
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <button className="px-2.5 py-1 rounded bg-purple-50 border border-purple-200 text-purple-700 hover:bg-purple-100 text-[10px] font-bold transition-all">
                      INSPECT
                    </button>
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
