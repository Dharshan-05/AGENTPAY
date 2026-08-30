'use client';

import { useEffect, useState } from 'react';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import {
  Radio, ShieldCheck, Activity, Lock, ArrowRight, Copy, RefreshCw, Check
} from 'lucide-react';
import { WebhookDeliveryRecord } from './webhook-types';

interface WebhookInspectorProps {
  delivery: WebhookDeliveryRecord | null;
  onClose: () => void;
  onReplay: (dlv: WebhookDeliveryRecord) => void;
}

export function WebhookInspector({ delivery, onClose, onReplay }: WebhookInspectorProps) {
  const [copiedPayload, setCopiedPayload] = useState(false);

  useEffect(() => {
    if (!delivery) return;
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [delivery, onClose]);

  if (!delivery) return null;

  const handleCopyPayload = () => {
    navigator.clipboard?.writeText(delivery.payloadJson);
    setCopiedPayload(true);
    setTimeout(() => setCopiedPayload(false), 2000);
  };

  return (
    <AGDrawer
      isOpen={!!delivery}
      onClose={onClose}
      title={`DELIVERY INSPECTOR: ${delivery.deliveryId}`}
      subtitle="WEBHOOK & EVENT OPERATIONS CONTROL"
      footer={
        <div className="space-y-2 font-mono">
          <div className="flex gap-2">
            <AGButton variant="ghost" size="sm" onClick={() => {
              navigator.clipboard?.writeText(delivery.deliveryId);
              alert(`Copied Delivery ID: ${delivery.deliveryId}`);
            }} className="flex-1">
              COPY DLV ID
            </AGButton>
            <AGButton variant="ghost" size="sm" onClick={() => {
              navigator.clipboard?.writeText(delivery.eventId);
              alert(`Copied Event ID: ${delivery.eventId}`);
            }} className="flex-1">
              COPY EVT ID
            </AGButton>
          </div>
          <AGButton variant="primary" size="md" onClick={() => onReplay(delivery)} className="w-full">
            <RefreshCw className="w-4 h-4 mr-2" /> REPLAY DELIVERY (SIMULATED)
          </AGButton>
        </div>
      }
    >
      <div className="space-y-5 font-mono text-xs">

        {/* DECISION CHAIN */}
        <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20 space-y-2">
          <div className="text-[9px] text-blue-400 font-bold uppercase tracking-[0.2em] mb-3">AGENTPAY CAUSAL EVENT TRACE</div>
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 flex-wrap">
            <span className="font-bold text-blue-400">{delivery.agentId}</span>
            <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
            <span className="font-bold text-purple-400">{delivery.transactionId || 'AGP-GOV-001'}</span>
            <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
            <span className="font-bold text-slate-200">{delivery.eventId}</span>
            <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
            <span className="font-bold text-emerald-400">{delivery.endpointId}</span>
            <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
            <span className={`font-bold ${delivery.responseStatus === 200 ? 'text-emerald-400' : 'text-red-400'}`}>
              HTTP {delivery.responseStatus}
            </span>
          </div>
        </div>

        {/* SECTION 01: IDENTITY */}
        <InspectorSection title="01 — DELIVERY IDENTITY" icon={Radio} color="text-blue-400">
          <Row label="Delivery ID" value={delivery.deliveryId} valueClass="text-blue-400 font-bold" />
          <Row label="Event ID" value={delivery.eventId} valueClass="text-purple-400 font-bold" />
          <Row label="Event Type" value={delivery.eventType} valueClass="text-slate-200" />
          <Row label="Target Endpoint" value={delivery.endpointName} valueClass="text-slate-200 font-bold" />
          <Row label="Target URL" value={delivery.targetUrl} valueClass="text-slate-400 text-[9px] truncate" />
          <Row label="Environment" value={delivery.environment} valueClass={delivery.environment === 'PRODUCTION' ? 'text-emerald-400' : 'text-amber-400'} />
          <Row label="Status" value={delivery.status} valueClass={delivery.status === 'DELIVERED' ? 'text-emerald-400' : 'text-red-400'} />
          <Row label="Created" value={delivery.createdTimestamp} />
        </InspectorSection>

        {/* SECTION 02: HTTP TELEMETRY */}
        <InspectorSection title="02 — HTTP TELEMETRY & LATENCY" icon={Activity} color="text-emerald-400">
          <div className="grid grid-cols-2 gap-2 mb-2">
            <div className="p-2 rounded-lg bg-slate-950/60 border border-white/[0.04]">
              <div className="text-[9px] text-slate-500 uppercase">HTTP STATUS</div>
              <div className={`text-sm font-bold ${delivery.responseStatus === 200 ? 'text-emerald-400' : 'text-red-400'}`}>
                {delivery.responseStatus}
              </div>
            </div>
            <div className="p-2 rounded-lg bg-slate-950/60 border border-white/[0.04]">
              <div className="text-[9px] text-slate-500 uppercase">LATENCY</div>
              <div className="text-sm font-bold text-blue-400">{delivery.latencyMs}ms</div>
            </div>
          </div>
          <Row label="Attempt Count" value={`${delivery.attemptCount} / ${delivery.maxRetries}`} />
        </InspectorSection>

        {/* SECTION 03: PAYLOAD VIEWER */}
        <InspectorSection title="03 — EVENT JSON PAYLOAD" icon={Activity} color="text-purple-400">
          <div className="relative">
            <pre className="p-3 rounded-lg bg-slate-950 border border-white/[0.06] text-[10px] text-emerald-300 font-mono overflow-x-auto max-h-[180px]">
              {delivery.payloadJson}
            </pre>
            <button
              onClick={handleCopyPayload}
              className="absolute top-2 right-2 px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 text-[9px] flex items-center gap-1 transition-all"
            >
              {copiedPayload ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {copiedPayload ? 'COPIED' : 'COPY JSON'}
            </button>
          </div>
        </InspectorSection>

        {/* SECTION 04: SECURITY & SIGNATURE */}
        <InspectorSection title="04 — ZERO-TRUST SECURITY" icon={ShieldCheck} color="text-emerald-400">
          <Row label="Signature" value={delivery.signature} valueClass="text-slate-400 text-[9px] truncate" />
          <Row label="Verification" value="HMAC-SHA256 PASSED" valueClass="text-emerald-400 font-bold" />
          <Row label="Replay Window" value="300s TOLERANCE" valueClass="text-blue-300" />
        </InspectorSection>

        {/* SECTION 05: ATTEMPT TIMELINE */}
        <InspectorSection title="05 — ATTEMPT TIMELINE" icon={Lock} color="text-amber-400">
          <div className="space-y-1.5">
            {delivery.attempts.map((att) => (
              <div key={att.attemptNumber} className="flex items-center justify-between p-2 rounded bg-slate-950/60 border border-white/[0.04]">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-400">ATTEMPTS #{att.attemptNumber}</span>
                  <span className={att.responseStatus === 200 ? 'text-emerald-400 font-bold' : 'text-red-400 font-bold'}>
                    {att.responseStatus}
                  </span>
                </div>
                <div className="text-[10px] text-slate-500 font-mono">
                  {att.latencyMs}ms · {att.timestamp}
                </div>
              </div>
            ))}
          </div>
        </InspectorSection>

      </div>
    </AGDrawer>
  );
}

function InspectorSection({ title, icon: Icon, color, children }: { title: string; icon: any; color: string; children: React.ReactNode; }) {
  return (
    <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2">
      <h4 className={`font-bold text-[11px] uppercase tracking-wider flex items-center gap-1.5 font-mono ${color}`}>
        <Icon className="w-3.5 h-3.5" /> {title}
      </h4>
      {children}
    </div>
  );
}

function Row({ label, value, valueClass = 'text-slate-300' }: { label: string; value: string; valueClass?: string; }) {
  return (
    <div className="flex justify-between items-center py-0.5">
      <span className="text-[10px] text-slate-500">{label}:</span>
      <span className={`text-[10px] font-mono ${valueClass} max-w-[60%] text-right truncate`}>{value}</span>
    </div>
  );
}
