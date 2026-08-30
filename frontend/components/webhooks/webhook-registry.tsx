'use client';

import { WebhookEndpoint } from './webhook-types';
import { AGBadge } from '@/components/ui/ag-badge';

interface WebhookRegistryProps {
  endpoints: WebhookEndpoint[];
  onSelect: (ep: WebhookEndpoint) => void;
}

export function WebhookRegistry({ endpoints, onSelect }: WebhookRegistryProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
            <th className="px-4 py-3 font-semibold">ENDPOINT ID</th>
            <th className="px-4 py-3 font-semibold">NAME &amp; URL</th>
            <th className="px-4 py-3 font-semibold">ENV</th>
            <th className="px-4 py-3 font-semibold">STATUS</th>
            <th className="px-4 py-3 font-semibold">EVENTS</th>
            <th className="px-4 py-3 font-semibold">SUCCESS RATE</th>
            <th className="px-4 py-3 font-semibold">P95 LATENCY</th>
            <th className="px-4 py-3 font-semibold">AUTH TYPE</th>
            <th className="px-4 py-3 font-semibold">LAST DELIVERY</th>
            <th className="px-4 py-3 font-semibold text-right">ACTION</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.04] text-xs">
          {endpoints.map((ep) => {
            const isHealthy = ep.status === 'HEALTHY' || ep.status === 'ACTIVE';
            const isDegraded = ep.status === 'DEGRADED';
            const isFailing = ep.status === 'FAILING';

            return (
              <tr
                key={ep.id}
                onClick={() => onSelect(ep)}
                className="hover:bg-slate-900/40 transition-colors cursor-pointer group"
              >
                <td className="px-4 py-3.5 font-bold text-blue-400 group-hover:text-blue-300">
                  {ep.endpointId}
                </td>
                <td className="px-4 py-3.5">
                  <div className="font-bold text-slate-200">{ep.name}</div>
                  <div className="text-[10px] text-slate-300 truncate max-w-[240px]">{ep.url}</div>
                </td>
                <td className="px-4 py-3.5">
                  <AGBadge status={ep.environment} size="sm" />
                </td>
                <td className="px-4 py-3.5">
                  <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                    isHealthy ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                    isDegraded ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                    isFailing ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                    'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      isHealthy ? 'bg-emerald-400 animate-pulse' : isDegraded ? 'bg-amber-400' : isFailing ? 'bg-red-400' : 'bg-slate-400'
                    }`} />
                    {ep.status}
                  </span>
                </td>
                <td className="px-4 py-3.5 font-bold text-slate-300">
                  {ep.subscribedEventsCount} TYPES
                </td>
                <td className="px-4 py-3.5 font-bold text-emerald-400">
                  {ep.successRate}%
                </td>
                <td className="px-4 py-3.5 text-slate-300">
                  {ep.p95LatencyMs}ms
                </td>
                <td className="px-4 py-3.5 text-blue-300 text-[10px]">
                  {ep.authType}
                </td>
                <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                  {ep.lastDelivery}
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
