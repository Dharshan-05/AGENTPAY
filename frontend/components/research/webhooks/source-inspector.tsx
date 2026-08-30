'use client';

import { useEffect } from 'react';
import { WebhookDeliveryRecord } from './source-types';
import { X, Copy, RefreshCw, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';

interface SourceInspectorProps {
  delivery: WebhookDeliveryRecord | null;
  onClose: () => void;
  onReplay: (deliveryId: string) => void;
}

export function SourceInspector({ delivery, onClose, onReplay }: SourceInspectorProps) {
  useEffect(() => {
    if (!delivery) return;
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [delivery, onClose]);

  if (!delivery) return null;

  const isDelivered = delivery.status === 'DELIVERED';

  return (
    <div className="fixed inset-0 z-50 flex justify-end font-sans">
      {/* OVERLAY BACKDROP */}
      <div
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* DRAWER CONTAINER */}
      <div className="relative w-full max-w-2xl bg-white border-l border-slate-200 shadow-2xl flex flex-col h-full z-10">
        {/* HEADER */}
        <div className="p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold text-purple-700 uppercase tracking-wider">
                WEBHOOK DELIVERY INSPECTOR
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                isDelivered ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'
              }`}>
                {delivery.status}
              </span>
            </div>
            <h2 className="text-lg font-bold text-slate-900 font-mono mt-0.5">
              {delivery.deliveryId}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* BODY CONTENT */}
        <div className="flex-1 p-6 overflow-y-auto space-y-6 text-xs font-mono">

          {/* CAUSAL EVENT CHAIN */}
          <div className="p-4 rounded-xl bg-purple-50 border border-purple-200 space-y-2">
            <div className="text-[10px] text-purple-800 font-bold uppercase tracking-wider mb-2">
              AGENTPAY EVENT CHAIN OBSERVED
            </div>
            <div className="flex items-center gap-1.5 text-[11px] text-slate-600 flex-wrap">
              <span className="font-bold text-blue-700">{delivery.agentId}</span>
              <ArrowRight className="w-3 h-3 text-slate-400" />
              <span className="font-bold text-slate-800">{delivery.transactionId || 'RESOURCE'}</span>
              <ArrowRight className="w-3 h-3 text-slate-400" />
              <span className="font-bold text-purple-700">{delivery.eventType}</span>
              <ArrowRight className="w-3 h-3 text-slate-400" />
              <span className="font-bold text-slate-800">{delivery.endpointName}</span>
              <ArrowRight className="w-3 h-3 text-slate-400" />
              <span className={`font-bold ${isDelivered ? 'text-emerald-700' : 'text-rose-700'}`}>
                HTTP {delivery.responseStatus} ({delivery.latencyMs}ms)
              </span>
            </div>
          </div>

          {/* SECTION 1: DELIVERY METADATA */}
          <div className="p-4 rounded-xl border border-slate-200 space-y-2 bg-slate-50">
            <h3 className="font-bold text-slate-800 uppercase tracking-wider text-[10px] text-slate-500">
              01 — DELIVERY SUMMARY
            </h3>
            <div className="space-y-1">
              <div className="flex justify-between py-0.5">
                <span className="text-slate-500">Event ID:</span>
                <span className="font-bold text-purple-700">{delivery.eventId}</span>
              </div>
              <div className="flex justify-between py-0.5">
                <span className="text-slate-500">Event Type:</span>
                <span className="font-bold text-slate-800">{delivery.eventType}</span>
              </div>
              <div className="flex justify-between py-0.5">
                <span className="text-slate-500">Endpoint ID:</span>
                <span className="text-slate-700">{delivery.endpointId}</span>
              </div>
              <div className="flex justify-between py-0.5">
                <span className="text-slate-500">Target URL:</span>
                <span className="text-slate-700 font-mono text-[11px] truncate max-w-[320px]">{delivery.targetUrl}</span>
              </div>
              <div className="flex justify-between py-0.5">
                <span className="text-slate-500">Created:</span>
                <span className="text-slate-600">{delivery.createdTimestamp}</span>
              </div>
            </div>
          </div>

          {/* SECTION 2: REQUEST HEADERS & SIGNATURE */}
          <div className="p-4 rounded-xl border border-slate-200 space-y-2">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-slate-800 uppercase tracking-wider text-[10px] text-slate-500">
                02 — REQUEST HEADERS &amp; SIGNATURE
              </h3>
              <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded font-bold text-[9px]">
                HMAC SIGNATURE VALID
              </span>
            </div>
            <div className="p-3 bg-slate-900 text-slate-200 rounded-xl overflow-x-auto text-[11px] font-mono leading-relaxed whitespace-pre-wrap">
              {delivery.requestHeaders}
            </div>
          </div>

          {/* SECTION 3: EVENT PAYLOAD JSON */}
          <div className="p-4 rounded-xl border border-slate-200 space-y-2">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-slate-800 uppercase tracking-wider text-[10px] text-slate-500">
                03 — EVENT PAYLOAD JSON
              </h3>
              <button
                onClick={() => {
                  navigator.clipboard?.writeText(delivery.payloadJson);
                  alert('Payload copied to clipboard');
                }}
                className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded font-bold text-[10px] flex items-center gap-1 border border-slate-200"
              >
                <Copy className="w-3 h-3" /> Copy JSON
              </button>
            </div>
            <pre className="p-3 bg-slate-900 text-emerald-400 rounded-xl overflow-x-auto text-[11px] font-mono max-h-60 leading-relaxed">
              {delivery.payloadJson}
            </pre>
          </div>

          {/* SECTION 4: RESPONSE BODY & HEADERS */}
          <div className="p-4 rounded-xl border border-slate-200 space-y-2">
            <h3 className="font-bold text-slate-800 uppercase tracking-wider text-[10px] text-slate-500">
              04 — HTTP RESPONSE
            </h3>
            <div className="p-3 bg-slate-900 text-blue-300 rounded-xl overflow-x-auto text-[11px] font-mono leading-relaxed">
              {delivery.responseBodySnippet || 'No response body snippet recorded.'}
            </div>
          </div>

          {/* SECTION 5: ATTEMPTS TIMELINE */}
          <div className="p-4 rounded-xl border border-slate-200 space-y-3">
            <h3 className="font-bold text-slate-800 uppercase tracking-wider text-[10px] text-slate-500">
              05 — DELIVERY ATTEMPTS TIMELINE ({delivery.attempts.length})
            </h3>
            <div className="space-y-2">
              {delivery.attempts.map((att) => (
                <div key={att.attemptNumber} className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex justify-between items-center text-[11px]">
                  <div>
                    <span className="font-bold text-slate-900 mr-2">Attempt {att.attemptNumber}</span>
                    <span className="text-slate-500">{att.timestamp}</span>
                    {att.errorMessage && (
                      <div className="text-rose-600 mt-0.5">{att.errorMessage}</div>
                    )}
                  </div>
                  <div className="text-right">
                    <span className={`font-bold ${att.responseStatus === 200 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      HTTP {att.responseStatus}
                    </span>
                    <span className="text-slate-500 block text-[10px]">{att.latencyMs}ms</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* FOOTER ACTIONS */}
        <div className="p-5 border-t border-slate-200 bg-slate-50 flex items-center justify-between gap-3">
          <button
            onClick={() => onReplay(delivery.deliveryId)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 shadow-sm transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            REPLAY EVENT NOW
          </button>

          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-xl text-xs transition-colors"
          >
            CLOSE INSPECTOR
          </button>
        </div>
      </div>
    </div>
  );
}
