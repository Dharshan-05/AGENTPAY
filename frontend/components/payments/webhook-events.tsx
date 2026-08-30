'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { WebhookEventRecord } from './types';
import { Webhook, Activity, CheckCircle2 } from 'lucide-react';

interface WebhookEventsProps {
  events: WebhookEventRecord[];
}

export function WebhookEvents({ events }: WebhookEventsProps) {
  return (
    <div className="space-y-6 font-mono text-xs">
      <AGCard className="space-y-4">
        <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
          <div>
            <span className="font-bold text-slate-100 flex items-center gap-2 text-sm">
              <Webhook className="w-4 h-4 text-blue-400" /> WEBHOOK & EVENT TELEMETRY STREAM
            </span>
            <p className="text-[10px] text-slate-400 mt-0.5">
              Live automated event notifications dispatched to merchant API endpoints
            </p>
          </div>

          <AGBadge status="POLICY_SECURE" label="ENDPOINT ACTIVE" />
        </div>

        {/* ENDPOINT CONFIG BOX */}
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1.5 text-[11px]">
          <div className="flex justify-between text-slate-400 text-[10px]">
            <span>Target Webhook Endpoint:</span>
            <span className="text-emerald-400 font-bold">HTTPS SSL Verified</span>
          </div>
          <div className="font-bold text-slate-100">https://api.merchant.com/v1/webhooks/agentpay</div>
          <div className="flex justify-between text-slate-400 text-[10px] pt-1 border-t border-white/[0.06]">
            <span>Signing Secret:</span>
            <span className="text-blue-400 font-mono">whsec_live_9981273918237498127</span>
          </div>
        </div>

        {/* LOGS TABLE */}
        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
            RECENT WEBHOOK DELIVERY LOGS
          </h4>

          <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.04] space-y-2.5 text-[11px]">
            {events.map((evt) => (
              <div key={evt.id} className="flex flex-wrap items-center justify-between gap-3 p-2.5 rounded-lg bg-slate-900/60 hover:bg-slate-900 transition-colors border border-white/[0.04]">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-slate-100">{evt.id}</span>
                  <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 text-[10px] font-bold">
                    {evt.event}
                  </span>
                  <span className="text-slate-400 text-[10px]">Ref: {evt.paymentId}</span>
                </div>

                <div className="flex items-center gap-4 text-[10px]">
                  <span className="text-emerald-400 font-bold">{evt.statusCode} {evt.status}</span>
                  <span className="text-slate-500">{evt.latency}</span>
                  <span className="text-slate-400">{evt.timestamp}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </AGCard>
    </div>
  );
}
