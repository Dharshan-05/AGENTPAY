'use client';

import { WebhookEventRecord } from './webhook-types';
import { AGBadge } from '@/components/ui/ag-badge';

interface WebhookEventsProps {
  events: WebhookEventRecord[];
  onSelect: (evt: WebhookEventRecord) => void;
}

export function WebhookEvents({ events, onSelect }: WebhookEventsProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
            <th className="px-4 py-3 font-semibold">EVENT ID</th>
            <th className="px-4 py-3 font-semibold">EVENT TYPE</th>
            <th className="px-4 py-3 font-semibold">RESOURCE REF</th>
            <th className="px-4 py-3 font-semibold">ORIGIN AGENT</th>
            <th className="px-4 py-3 font-semibold">SEVERITY</th>
            <th className="px-4 py-3 font-semibold">DELIVERIES</th>
            <th className="px-4 py-3 font-semibold">CREATED</th>
            <th className="px-4 py-3 font-semibold text-right">ACTION</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.04] text-xs">
          {events.map((evt) => (
            <tr
              key={evt.id}
              onClick={() => onSelect(evt)}
              className="hover:bg-slate-900/40 transition-colors cursor-pointer group"
            >
              <td className="px-4 py-3.5 font-bold text-purple-400 group-hover:text-purple-300">
                {evt.eventId}
              </td>
              <td className="px-4 py-3.5 font-bold text-blue-400">
                {evt.eventType}
              </td>
              <td className="px-4 py-3.5 text-slate-300">
                {evt.resourceId}
              </td>
              <td className="px-4 py-3.5 text-slate-400">
                <div>{evt.agentId}</div>
                <div className="text-[10px] text-slate-600 font-sans">{evt.agentName}</div>
              </td>
              <td className="px-4 py-3.5">
                <AGBadge status={evt.severity} size="sm" />
              </td>
              <td className="px-4 py-3.5 text-slate-300 font-bold">
                {evt.deliveryCount} DISPATCHED
              </td>
              <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                {evt.createdTimestamp}
              </td>
              <td className="px-4 py-3.5 text-right">
                <button className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[10px] font-bold transition-all">
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
