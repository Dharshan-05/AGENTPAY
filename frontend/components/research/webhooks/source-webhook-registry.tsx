'use client';

import { WebhookEndpoint } from './source-types';

interface SourceWebhookRegistryProps {
  endpoints: WebhookEndpoint[];
  onSelect: (ep: WebhookEndpoint) => void;
}

export function SourceWebhookRegistry({ endpoints, onSelect }: SourceWebhookRegistryProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 font-mono text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">ENDPOINT ID</th>
              <th className="px-4 py-3 font-semibold">NAME &amp; URL</th>
              <th className="px-4 py-3 font-semibold">ENV</th>
              <th className="px-4 py-3 font-semibold">EVENTS</th>
              <th className="px-4 py-3 font-semibold">STATUS</th>
              <th className="px-4 py-3 font-semibold">HEALTH</th>
              <th className="px-4 py-3 font-semibold">P95 LATENCY</th>
              <th className="px-4 py-3 font-semibold">SUCCESS %</th>
              <th className="px-4 py-3 font-semibold">AUTH TYPE</th>
              <th className="px-4 py-3 font-semibold">SECRET STATUS</th>
              <th className="px-4 py-3 font-semibold text-right">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-mono text-xs">
            {endpoints.map((ep) => {
              const isHealthy = ep.status === 'HEALTHY' || ep.status === 'ACTIVE';
              const isDegraded = ep.status === 'DEGRADED';
              const isFailing = ep.status === 'FAILING';

              return (
                <tr
                  key={ep.id}
                  onClick={() => onSelect(ep)}
                  className="hover:bg-slate-50 transition-colors cursor-pointer group"
                >
                  <td className="px-4 py-3.5 font-bold text-purple-700 group-hover:text-purple-900">
                    {ep.endpointId}
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="font-bold text-slate-900 font-sans">{ep.name}</div>
                    <div className="text-[11px] text-slate-500 font-mono truncate max-w-[280px]">{ep.url}</div>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      ep.environment === 'PRODUCTION' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      ep.environment === 'STAGING' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                      'bg-slate-100 text-slate-600 border-slate-200'
                    }`}>
                      {ep.environment}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 font-bold text-slate-700">
                    {ep.subscribedEventsCount} TYPES
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                      isHealthy ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      isDegraded ? 'bg-amber-50 text-amber-700 border-amber-200' :
                      isFailing ? 'bg-rose-50 text-rose-700 border-rose-200' :
                      'bg-slate-100 text-slate-600 border-slate-200'
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${
                        isHealthy ? 'bg-emerald-500' : isDegraded ? 'bg-amber-500' : isFailing ? 'bg-rose-500' : 'bg-slate-400'
                      }`} />
                      {ep.status}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`font-bold ${
                      ep.healthScore >= 99 ? 'text-emerald-600' : ep.healthScore >= 90 ? 'text-amber-600' : 'text-rose-600'
                    }`}>
                      {ep.healthScore}%
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-slate-600">
                    {ep.p95LatencyMs}ms
                  </td>
                  <td className="px-4 py-3.5 font-bold text-slate-800">
                    {ep.successRate}%
                  </td>
                  <td className="px-4 py-3.5 text-slate-600 text-[11px]">
                    {ep.authType}
                  </td>
                  <td className="px-4 py-3.5 text-slate-500 text-[11px]">
                    <div>{ep.secretMasked}</div>
                    <div className="text-[9px] text-slate-400">Due in {ep.secretRotationDays}d</div>
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <button className="px-2.5 py-1 rounded bg-purple-50 border border-purple-200 text-purple-700 hover:bg-purple-100 text-[10px] font-bold transition-all">
                      MANAGE
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
