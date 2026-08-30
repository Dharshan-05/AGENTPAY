'use client';

import { WebhookSubscription } from './webhook-types';
import { AGBadge } from '@/components/ui/ag-badge';

interface WebhookSubscriptionsProps {
  subscriptions: WebhookSubscription[];
}

export function WebhookSubscriptions({ subscriptions }: WebhookSubscriptionsProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
            <th className="px-4 py-3 font-semibold">SUB ID</th>
            <th className="px-4 py-3 font-semibold">TARGET ENDPOINT</th>
            <th className="px-4 py-3 font-semibold">EVENT PATTERN</th>
            <th className="px-4 py-3 font-semibold">FILTER RULE</th>
            <th className="px-4 py-3 font-semibold">ENV</th>
            <th className="px-4 py-3 font-semibold">STATUS</th>
            <th className="px-4 py-3 font-semibold">LAST TRIGGERED</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.04] text-xs">
          {subscriptions.map((sub) => (
            <tr key={sub.id} className="hover:bg-slate-900/40 transition-colors">
              <td className="px-4 py-3.5 font-bold text-blue-400">
                {sub.subscriptionId}
              </td>
              <td className="px-4 py-3.5 font-bold text-slate-300">
                {sub.endpointName}
              </td>
              <td className="px-4 py-3.5 font-bold text-purple-400">
                {sub.eventPattern}
              </td>
              <td className="px-4 py-3.5 text-slate-400 text-[11px]">
                {sub.filterRule}
              </td>
              <td className="px-4 py-3.5">
                <AGBadge status={sub.environment} size="sm" />
              </td>
              <td className="px-4 py-3.5">
                <AGBadge status={sub.status} size="sm" />
              </td>
              <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                {sub.lastTriggered}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
