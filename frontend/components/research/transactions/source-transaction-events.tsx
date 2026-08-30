'use client';

import { SourceTransactionEvent, DeliveryStatus } from './source-types';
import { CheckCircle2, XCircle, Loader2, Clock, Zap } from 'lucide-react';

interface SourceTransactionEventsProps {
  events: SourceTransactionEvent[];
}

function deliveryBadge(status: DeliveryStatus) {
  const map: Record<DeliveryStatus, { bg: string; text: string; icon: React.ReactNode }> = {
    DELIVERED: { bg: 'bg-emerald-100', text: 'text-emerald-800', icon: <CheckCircle2 className="w-3 h-3" /> },
    PENDING: { bg: 'bg-slate-100', text: 'text-slate-700', icon: <Clock className="w-3 h-3" /> },
    FAILED: { bg: 'bg-rose-100', text: 'text-rose-800', icon: <XCircle className="w-3 h-3" /> },
    RETRYING: { bg: 'bg-amber-100', text: 'text-amber-800', icon: <Loader2 className="w-3 h-3 animate-spin" /> },
  };
  const s = map[status];
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${s.bg} ${s.text}`}>
      {s.icon}
      {status}
    </span>
  );
}

function eventTypeColor(type: string) {
  if (type.includes('FAILED') || type.includes('ERROR')) return 'text-rose-700 bg-rose-50';
  if (type.includes('APPROVED') || type.includes('DELIVERED') || type.includes('COMPLETED') || type.includes('MATCHED')) return 'text-emerald-700 bg-emerald-50';
  if (type.includes('REQUESTED') || type.includes('CREATED') || type.includes('SCORED') || type.includes('EVALUATED')) return 'text-blue-700 bg-blue-50';
  if (type.includes('CAPTURED') || type.includes('CONFIRMED') || type.includes('VERIFIED') || type.includes('AUTHENTICATED')) return 'text-teal-700 bg-teal-50';
  return 'text-slate-700 bg-slate-100';
}

export function SourceTransactionEvents({ events }: SourceTransactionEventsProps) {
  const delivered = events.filter(e => e.deliveryStatus === 'DELIVERED').length;
  const failed = events.filter(e => e.deliveryStatus === 'FAILED').length;
  const avgLatency = events.length > 0
    ? Math.round(events.reduce((a, e) => a + e.latencyMs, 0) / events.length)
    : 0;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans text-xs">
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm">Webhook &amp; API Event Audit Stream</h3>
          <p className="text-[11px] text-slate-500 mt-0.5">
            {events.length} events · {delivered} delivered · {failed} failed · avg latency {avgLatency}ms
          </p>
        </div>
        <div className="text-[10px] text-slate-400 font-mono">SOURCE: Hyperswitch Events · Kill Bill Notifications · Lago Webhooks</div>
      </div>

      {/* Summary */}
      <div className="flex items-center gap-4 px-5 py-3 bg-slate-50 border-b border-slate-100">
        <div className="flex items-center gap-1.5 text-[11px]">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
          <span className="font-bold text-emerald-700">{delivered}</span>
          <span className="text-slate-500">Delivered</span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px]">
          <XCircle className="w-3.5 h-3.5 text-rose-500" />
          <span className="font-bold text-rose-700">{failed}</span>
          <span className="text-slate-500">Failed</span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px]">
          <Zap className="w-3.5 h-3.5 text-slate-500" />
          <span className="font-bold text-slate-700">{avgLatency}ms</span>
          <span className="text-slate-500">Avg Latency</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[1000px]">
          <thead>
            <tr className="border-b border-slate-100 text-slate-500 bg-slate-50 text-[10px] uppercase tracking-wide font-bold">
              <th className="px-4 py-3">EVENT ID &amp; TIMESTAMP</th>
              <th className="px-4 py-3">TRANSACTION ID</th>
              <th className="px-4 py-3">EVENT TYPE</th>
              <th className="px-4 py-3">SOURCE GATEWAY</th>
              <th className="px-4 py-3 text-right">LATENCY</th>
              <th className="px-4 py-3">STATUS</th>
              <th className="px-4 py-3 text-right">HTTP</th>
              <th className="px-4 py-3 text-right">RETRIES</th>
              <th className="px-4 py-3">AUDIT HASH</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {events.map((e) => (
              <tr key={e.id} className={`hover:bg-slate-50/50 transition-colors ${e.deliveryStatus === 'FAILED' ? 'bg-rose-50/20' : ''}`}>
                <td className="px-4 py-3">
                  <div className="font-bold font-mono text-[11px] text-slate-900">{e.eventId}</div>
                  <div className="text-slate-500 font-mono text-[9px] mt-0.5">{e.timestamp}</div>
                </td>
                <td className="px-4 py-3 font-bold text-blue-700 font-mono text-[11px]">{e.transactionId}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded font-mono text-[9px] font-bold ${eventTypeColor(e.eventType)}`}>
                    {e.eventType}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-700 text-[10px] font-semibold">{e.sourceGateway}</td>
                <td className="px-4 py-3 text-right font-mono text-[11px]">
                  <span className={e.latencyMs > 200 ? 'text-amber-600 font-bold' : 'text-slate-700'}>
                    {e.latencyMs}ms
                  </span>
                </td>
                <td className="px-4 py-3">{deliveryBadge(e.deliveryStatus)}</td>
                <td className="px-4 py-3 text-right font-mono text-[11px]">
                  <span className={e.responseStatus && e.responseStatus >= 400 ? 'text-rose-600 font-bold' : 'text-emerald-600 font-bold'}>
                    {e.responseStatus || '—'}
                  </span>
                </td>
                <td className="px-4 py-3 text-right font-mono text-[11px]">
                  <span className={e.retryCount > 0 ? 'text-amber-600 font-bold' : 'text-slate-400'}>
                    {e.retryCount}
                  </span>
                </td>
                <td className="px-4 py-3 font-mono text-[9px] text-slate-400 max-w-[160px] truncate">
                  {e.auditHash}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 text-[10px] text-slate-400 font-mono">
        Event chain: PAYMENT_INTENT.CREATED → AGENT.AUTHENTICATED → CAPABILITY.VERIFIED → POLICY.EVALUATED → RISK.SCORED → AUTHORIZATION.APPROVED → PAYMENT.CAPTURED → PROCESSOR.CONFIRMED → WEBHOOK.DELIVERED → SETTLEMENT.MATCHED
      </div>
    </div>
  );
}
