'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { WebhookEndpoint, WebhookEventRecord } from './developers-types';
import { Webhook, CheckCircle2 } from 'lucide-react';

interface WebhookEventsProps {
  webhooks: WebhookEndpoint[];
  events: WebhookEventRecord[];
  onSelectEvent: (event: WebhookEventRecord) => void;
}

export function WebhookEvents({ webhooks, events, onSelectEvent }: WebhookEventsProps) {
  return (
    <div className="space-y-6 font-mono text-xs">
      
      {/* ENDPOINTS LIST */}
      <AGCard className="space-y-4">
        <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Webhook className="w-4 h-4 text-blue-400" /> REGISTERED WEBHOOK ENDPOINTS
            </h3>
            <p className="text-[10px] text-slate-400">Cryptographically signed HMAC SHA-256 event notification destinations</p>
          </div>
          <AGBadge status="POLICY_SECURE" label="HMAC SIGNING ACTIVE" />
        </div>

        <div className="space-y-3">
          {webhooks.map((w) => (
            <div key={w.id} className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-100">{w.url}</span>
                  <AGBadge status={w.status === 'ACTIVE' ? 'APPROVED' : 'PENDING'} label={`● ${w.status}`} />
                </div>
                <span className="text-[10px] text-slate-400">Delivery Rate: <span className="text-emerald-400 font-bold">{w.deliveryRate}</span></span>
              </div>

              <div className="flex flex-wrap gap-1.5 pt-1">
                {w.events.map((evt) => (
                  <span key={evt} className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 text-[10px] font-bold">
                    {evt}
                  </span>
                ))}
              </div>

              <div className="flex justify-between items-center text-[10px] text-slate-400 pt-2 border-t border-white/[0.06]">
                <span>Signing Secret: <span className="text-blue-400 font-mono">{w.signingSecret}</span></span>
                <span className="text-slate-500">Latency: {w.latency}</span>
              </div>
            </div>
          ))}
        </div>
      </AGCard>

      {/* RECENT EVENT DELIVERIES */}
      <AGCard className="space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
          <span className="font-bold text-slate-100 text-sm">RECENT EVENT DELIVERY STREAM</span>
          <span className="text-[10px] text-slate-400">Click event for Webhook Inspector</span>
        </div>

        <div className="space-y-2">
          {events.map((evt) => (
            <div
              key={evt.id}
              onClick={() => onSelectEvent(evt)}
              className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-950 hover:bg-slate-900 border border-white/[0.04] cursor-pointer transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="font-bold text-slate-100">{evt.id}</span>
                <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 text-[10px] font-bold">
                  {evt.event}
                </span>
              </div>

              <div className="flex items-center gap-4 text-[10px]">
                <span className="text-emerald-400 font-bold">{evt.statusCode} {evt.status}</span>
                <span className="text-slate-500">{evt.latency}</span>
                <span className="text-slate-400">{evt.timestamp}</span>
              </div>
            </div>
          ))}
        </div>
      </AGCard>

    </div>
  );
}
