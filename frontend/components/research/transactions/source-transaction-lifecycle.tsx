'use client';

import { LifecycleStep, LifecycleStepStatus } from './source-types';
import { CheckCircle2, XCircle, Clock, MinusCircle, Loader2 } from 'lucide-react';

interface SourceTransactionLifecycleProps {
  steps: LifecycleStep[];
  transactionId: string;
  transactionStatus: string;
}

function stepIcon(status: LifecycleStepStatus) {
  switch (status) {
    case 'COMPLETED':
      return <CheckCircle2 className="w-5 h-5 text-emerald-600" />;
    case 'FAILED':
      return <XCircle className="w-5 h-5 text-rose-600" />;
    case 'ACTIVE':
      return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
    case 'SKIPPED':
      return <MinusCircle className="w-5 h-5 text-slate-300" />;
    case 'PENDING':
      return <Clock className="w-5 h-5 text-slate-300" />;
    default:
      return <Clock className="w-5 h-5 text-slate-300" />;
  }
}

function stepLineColor(status: LifecycleStepStatus): string {
  switch (status) {
    case 'COMPLETED': return 'border-emerald-400';
    case 'FAILED': return 'border-rose-400';
    case 'ACTIVE': return 'border-blue-400';
    case 'SKIPPED': return 'border-slate-200';
    case 'PENDING': return 'border-slate-200';
    default: return 'border-slate-200';
  }
}

function stepBg(status: LifecycleStepStatus): string {
  switch (status) {
    case 'COMPLETED': return 'bg-emerald-50 border-emerald-200';
    case 'FAILED': return 'bg-rose-50 border-rose-200';
    case 'ACTIVE': return 'bg-blue-50 border-blue-200';
    case 'SKIPPED': return 'bg-slate-50 border-slate-100';
    case 'PENDING': return 'bg-white border-slate-100';
    default: return 'bg-white border-slate-100';
  }
}

export function SourceTransactionLifecycle({
  steps,
  transactionId,
  transactionStatus,
}: SourceTransactionLifecycleProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans">
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm">Transaction Lifecycle</h3>
          <p className="text-[11px] text-slate-500 mt-0.5">
            10-stage lifecycle pipeline · {transactionId} · Final status:{' '}
            <span className="font-bold text-slate-700">{transactionStatus}</span>
          </p>
        </div>
        <div className="text-[10px] text-slate-400 font-mono">
          SOURCE: Kill Bill Payment State · Hyperswitch Lifecycle · Lago Financial Events
        </div>
      </div>

      <div className="p-5">
        {/* Summary bar */}
        <div className="flex items-center gap-1.5 mb-6 overflow-x-auto pb-2">
          {steps.map((step, i) => (
            <div key={step.stepId} className="flex items-center gap-1.5 flex-shrink-0">
              <div className={`flex flex-col items-center gap-0.5`}>
                <div className={`w-7 h-7 rounded-full flex items-center justify-center border-2 ${
                  step.status === 'COMPLETED' ? 'bg-emerald-500 border-emerald-500' :
                  step.status === 'FAILED' ? 'bg-rose-500 border-rose-500' :
                  step.status === 'ACTIVE' ? 'bg-blue-500 border-blue-500' :
                  step.status === 'SKIPPED' ? 'bg-slate-200 border-slate-200' :
                  'bg-white border-slate-300'
                }`}>
                  <span className="text-white text-[10px] font-bold">{step.stepNumber}</span>
                </div>
                <span className="text-[9px] text-slate-500 whitespace-nowrap max-w-[60px] text-center truncate">{step.label}</span>
              </div>
              {i < steps.length - 1 && (
                <div className={`w-6 h-0.5 flex-shrink-0 mt-[-10px] ${
                  step.status === 'COMPLETED' ? 'bg-emerald-400' :
                  step.status === 'FAILED' ? 'bg-rose-300' :
                  'bg-slate-200'
                }`} />
              )}
            </div>
          ))}
        </div>

        {/* Detail cards */}
        <div className="space-y-2">
          {steps.map((step) => (
            <div
              key={step.stepId}
              className={`rounded-xl border p-3.5 ${stepBg(step.status)}`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">{stepIcon(step.status)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold text-slate-400 font-mono">STEP {String(step.stepNumber).padStart(2, '0')}</span>
                      <h4 className="font-bold text-slate-800 text-xs">{step.label}</h4>
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                        step.status === 'COMPLETED' ? 'bg-emerald-200 text-emerald-800' :
                        step.status === 'FAILED' ? 'bg-rose-200 text-rose-800' :
                        step.status === 'SKIPPED' ? 'bg-slate-200 text-slate-600' :
                        step.status === 'ACTIVE' ? 'bg-blue-200 text-blue-800' :
                        'bg-slate-100 text-slate-500'
                      }`}>
                        {step.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-[10px] text-slate-400 font-mono">
                      {step.timestamp && <span>⏱ {step.timestamp}</span>}
                      {step.latencyMs && step.latencyMs < 10000 && <span>{step.latencyMs}ms</span>}
                      {step.latencyMs && step.latencyMs >= 10000 && <span>{(step.latencyMs / 1000).toFixed(0)}s</span>}
                    </div>
                  </div>
                  <p className="text-[11px] text-slate-600 mt-1">{step.description}</p>
                  <div className="text-[10px] text-slate-400 mt-1">Actor: <span className="font-semibold text-slate-600">{step.actor}</span></div>
                  {step.metadata && Object.keys(step.metadata).length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {Object.entries(step.metadata).map(([k, v]) => (
                        <div key={k} className="bg-white/80 border border-slate-200 rounded px-2 py-0.5 text-[9px] font-mono">
                          <span className="text-slate-400">{k}: </span>
                          <span className="font-bold text-slate-700">{v}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 text-[10px] text-slate-400 font-mono">
        Pipeline: INTENT_CREATED → IDENTITY_VERIFIED → CAPABILITY_CHECK → POLICY_EVALUATED → RISK_EVALUATED → AUTHORIZATION → CAPTURE → PROCESSOR_CONFIRMATION → SETTLEMENT → AUDIT
      </div>
    </div>
  );
}
