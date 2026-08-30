'use client';

import { WebhookEventRecord } from './source-types';

interface SourceEventCatalogProps {
  events: WebhookEventRecord[];
  onSelect: (ev: WebhookEventRecord) => void;
}

export function SourceEventCatalog({ events, onSelect }: SourceEventCatalogProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 font-mono text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">EVENT ID</th>
              <th className="px-4 py-3 font-semibold">EVENT TYPE</th>
              <th className="px-4 py-3 font-semibold">RESOURCE</th>
              <th className="px-4 py-3 font-semibold">ORIGIN AGENT</th>
              <th className="px-4 py-3 font-semibold">SEVERITY</th>
              <th className="px-4 py-3 font-semibold">ENV</th>
              <th className="px-4 py-3 font-semibold">DELIVERIES</th>
              <th className="px-4 py-3 font-semibold">TIMESTAMP</th>
              <th className="px-4 py-3 font-semibold text-right">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-mono text-xs">
            {events.map((ev) => (
              <tr
                key={ev.id}
                onClick={() => onSelect(ev)}
                className="hover:bg-slate-50 transition-colors cursor-pointer group"
              >
                <td className="px-4 py-3.5 font-bold text-slate-800">
                  {ev.eventId}
                </td>
                <td className="px-4 py-3.5 font-bold text-purple-700">
                  {ev.eventType}
                </td>
                <td className="px-4 py-3.5 text-slate-600">
                  <div>{ev.resourceType}</div>
                  <div className="text-[10px] text-slate-400">{ev.resourceId}</div>
                </td>
                <td className="px-4 py-3.5 text-slate-700">
                  <div>{ev.agentId}</div>
                  <div className="text-[10px] text-slate-400">{ev.agentName}</div>
                </td>
                <td className="px-4 py-3.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                    ev.severity === 'CRITICAL' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                    ev.severity === 'WARNING' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                    'bg-blue-50 text-blue-700 border-blue-200'
                  }`}>
                    {ev.severity}
                  </span>
                </td>
                <td className="px-4 py-3.5 text-slate-500">
                  {ev.environment}
                </td>
                <td className="px-4 py-3.5 font-bold text-emerald-600">
                  {ev.deliveryCount} ENDPOINTS
                </td>
                <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                  {ev.createdTimestamp}
                </td>
                <td className="px-4 py-3.5 text-right">
                  <button className="px-2.5 py-1 rounded bg-slate-100 border border-slate-200 text-slate-700 hover:bg-slate-200 text-[10px] font-bold transition-all">
                    INSPECT PAYLOAD
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
