'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { WebhookEventRecord } from './developers-types';
import { Webhook, Copy, Check, RotateCw } from 'lucide-react';
import { useState } from 'react';

interface WebhookInspectorProps {
  event: WebhookEventRecord | null;
  onClose: () => void;
}

export function WebhookInspector({ event, onClose }: WebhookInspectorProps) {
  const [copiedId, setCopiedId] = useState(false);

  if (!event) return null;

  const copyId = () => {
    navigator.clipboard.writeText(event.id);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  return (
    <AGDrawer
      isOpen={!!event}
      onClose={onClose}
      title={`WEBHOOK INSPECTOR: ${event.id}`}
      subtitle="REAL-TIME EVENT DISPATCH & HMAC SIGNATURE AUDIT"
      footer={
        <div className="space-y-3 font-mono">
          <div className="grid grid-cols-2 gap-2">
            <AGButton variant="primary" size="md" onClick={() => alert(`Simulated replay for ${event.id}`)}>
              REPLAY EVENT
            </AGButton>
            <AGButton variant="secondary" size="md" onClick={onClose}>
              CLOSE INSPECTOR
            </AGButton>
          </div>
          <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-white/[0.08]">
            <span>Event Signature Verified</span>
            <span>200 OK Response</span>
          </div>
        </div>
      }
    >
      <div className="space-y-6 font-mono text-xs">
        
        <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase">EVENT TYPE</span>
            <span className="text-base font-bold text-blue-400">{event.event}</span>
          </div>
          <AGBadge status="APPROVED" label={`● ${event.statusCode} ${event.status}`} />
        </div>

        <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Destination Endpoint:</span>
            <span className="text-slate-200 font-bold">{event.endpointUrl}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Delivery Latency:</span>
            <span className="text-emerald-400 font-bold">{event.latency}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Attempts Count:</span>
            <span className="text-slate-300">{event.attempts} Attempt</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Timestamp:</span>
            <span className="text-slate-400">{event.timestamp}</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950 border border-white/[0.04] space-y-1 text-[10px]">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">HMAC SHA-256 Signature:</span>
            <button onClick={copyId} className="text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1">
              {copiedId ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {copiedId ? 'COPIED' : 'COPY ID'}
            </button>
          </div>
          <div className="text-emerald-400 font-mono text-[9px] break-all">{event.signature}</div>
        </div>

        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
            EVENT PAYLOAD (JSON)
          </h4>
          <pre className="p-3 rounded-xl bg-slate-950 border border-white/[0.04] text-[10px] text-emerald-400 overflow-x-auto">
            {JSON.stringify(event.payload, null, 2)}
          </pre>
        </div>

      </div>
    </AGDrawer>
  );
}
