'use client';

import { SourceWebhookEndpointRecord } from './source-types';
import { Webhook, CheckCircle2, Shield, Plus } from 'lucide-react';

interface SourceWebhooksProps {
  webhooks: SourceWebhookEndpointRecord[];
}

export function SourceWebhooks({ webhooks }: SourceWebhooksProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Webhook className="w-4 h-4 text-blue-600" />
            Webhook Subscriptions & Endpoint Routing
          </h3>
          <p className="text-xs text-slate-500">Excavated webhook configuration panel architecture</p>
        </div>

        <button className="px-3 py-1.5 bg-slate-900 text-white text-xs font-semibold rounded-xl hover:bg-slate-800 flex items-center gap-1">
          <Plus className="w-3.5 h-3.5" /> Add Endpoint
        </button>
      </div>

      <div className="space-y-3 font-mono text-xs">
        {webhooks.map((w) => (
          <div key={w.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900">{w.url}</span>
                <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded">
                  {w.status}
                </span>
              </div>

              <span className="text-[10px] text-slate-500 font-sans">Created {w.created}</span>
            </div>

            <div className="flex flex-wrap gap-1.5 pt-1">
              {w.events.map((evt) => (
                <span key={evt} className="px-2 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 text-[10px] font-bold rounded">
                  {evt}
                </span>
              ))}
            </div>

            <div className="flex justify-between items-center text-[10px] text-slate-500 pt-2 border-t border-slate-200">
              <span>Signing Secret: <span className="font-bold text-slate-700">{w.signingSecret}</span></span>
              <span className="text-emerald-600 font-bold flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> SSL Verified</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
