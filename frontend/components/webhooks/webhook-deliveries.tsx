'use client';

import { WebhookDeliveryRecord } from './webhook-types';
import { AGBadge } from '@/components/ui/ag-badge';

interface WebhookDeliveriesProps {
  deliveries: WebhookDeliveryRecord[];
  onSelect: (dlv: WebhookDeliveryRecord) => void;
}

export function WebhookDeliveries({ deliveries, onSelect }: WebhookDeliveriesProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
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
        <tbody className="divide-y divide-white/[0.04] text-xs">
          {deliveries.map((dlv) => {
            const isSuccess = dlv.status === 'DELIVERED';
            const isExhausted = dlv.status === 'EXHAUSTED';

            return (
              <tr
                key={dlv.id}
                onClick={() => onSelect(dlv)}
                className="hover:bg-slate-900/40 transition-colors cursor-pointer group"
              >
                <td className="px-4 py-3.5 font-bold text-blue-400 group-hover:text-blue-300">
                  {dlv.deliveryId}
                </td>
                <td className="px-4 py-3.5 text-slate-300">
                  {dlv.eventType}
                </td>
                <td className="px-4 py-3.5 text-slate-400">
                  <div className="font-bold text-slate-300">{dlv.endpointName}</div>
                  <div className="text-[10px] text-slate-600">{dlv.endpointId}</div>
                </td>
                <td className="px-4 py-3.5">
                  <AGBadge status={dlv.status} size="sm" />
                </td>
                <td className="px-4 py-3.5 font-bold">
                  <span className={dlv.responseStatus === 200 ? 'text-emerald-400' : 'text-red-400'}>
                    {dlv.responseStatus}
                  </span>
                </td>
                <td className="px-4 py-3.5 font-bold text-slate-300">
                  {dlv.latencyMs}ms
                </td>
                <td className="px-4 py-3.5 text-slate-400">
                  {dlv.attemptCount} / {dlv.maxRetries}
                </td>
                <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                  {dlv.createdTimestamp}
                </td>
                <td className="px-4 py-3.5 text-right">
                  <button className="px-2.5 py-1 rounded bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 text-[10px] font-bold transition-all">
                    INSPECT
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
