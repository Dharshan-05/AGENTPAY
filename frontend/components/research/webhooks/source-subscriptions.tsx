'use client';

import { WebhookSubscription } from './source-types';

interface SourceSubscriptionsProps {
  subscriptions: WebhookSubscription[];
}

export function SourceSubscriptions({ subscriptions }: SourceSubscriptionsProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 font-mono text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">SUBSCRIPTION ID</th>
              <th className="px-4 py-3 font-semibold">ENDPOINT</th>
              <th className="px-4 py-3 font-semibold">EVENT PATTERN</th>
              <th className="px-4 py-3 font-semibold">FILTER RULE</th>
              <th className="px-4 py-3 font-semibold">ENV</th>
              <th className="px-4 py-3 font-semibold">STATUS</th>
              <th className="px-4 py-3 font-semibold">LAST TRIGGERED</th>
              <th className="px-4 py-3 font-semibold">CREATED</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-mono text-xs">
            {subscriptions.map((sub) => (
              <tr key={sub.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3.5 font-bold text-slate-800">
                  {sub.subscriptionId}
                </td>
                <td className="px-4 py-3.5 text-slate-700 font-sans font-medium">
                  {sub.endpointName}
                </td>
                <td className="px-4 py-3.5 font-bold text-purple-700">
                  {sub.eventPattern}
                </td>
                <td className="px-4 py-3.5 text-slate-600 text-[11px]">
                  {sub.filterRule}
                </td>
                <td className="px-4 py-3.5">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-600 border border-slate-200">
                    {sub.environment}
                  </span>
                </td>
                <td className="px-4 py-3.5">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                    sub.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-100 text-slate-600 border-slate-200'
                  }`}>
                    {sub.status}
                  </span>
                </td>
                <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                  {sub.lastTriggered}
                </td>
                <td className="px-4 py-3.5 text-slate-400 text-[10px]">
                  {sub.createdTimestamp}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
