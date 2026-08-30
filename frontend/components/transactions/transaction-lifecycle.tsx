'use client';

import { TxnLifecycleStep } from './transaction-types';
import { PRODUCTION_LIFECYCLE_SETTLED, PRODUCTION_LIFECYCLE_BLOCKED } from './transaction-data';

interface TransactionLifecycleProps {
  selectedLifecycle: 'SETTLED' | 'BLOCKED';
  onLifecycleChange: (v: 'SETTLED' | 'BLOCKED') => void;
}

export function TransactionLifecycle({
  selectedLifecycle,
  onLifecycleChange,
}: TransactionLifecycleProps) {
  const steps: TxnLifecycleStep[] = selectedLifecycle === 'SETTLED' ? PRODUCTION_LIFECYCLE_SETTLED : PRODUCTION_LIFECYCLE_BLOCKED;

  return (
    <div className="space-y-6">
      {/* TOGGLE LIFECYCLE SCENARIO */}
      <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl">
        <div>
          <h3 className="font-display font-bold text-sm text-slate-100">LIFECYCLE SEQUENCE SIMULATOR</h3>
          <p className="text-xs font-mono text-slate-400 mt-0.5">
            Visualize the full 10-stage causal execution chain from Agent Payment Intent to Final Ledger State.
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs">
          <button
            onClick={() => onLifecycleChange('SETTLED')}
            className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
              selectedLifecycle === 'SETTLED'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-[0_0_15px_rgba(16,185,129,0.2)]'
                : 'bg-slate-950 text-slate-400 border border-white/[0.08] hover:text-slate-200'
            }`}
          >
            ● SETTLED CHAIN (TXN-AGP-91F2)
          </button>
          <button
            onClick={() => onLifecycleChange('BLOCKED')}
            className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
              selectedLifecycle === 'BLOCKED'
                ? 'bg-red-500/20 text-red-400 border border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.2)]'
                : 'bg-slate-950 text-slate-400 border border-white/[0.08] hover:text-slate-200'
            }`}
          >
            ■ POLICY BLOCKED CHAIN (TXN-AGP-11A8)
          </button>
        </div>
      </div>

      {/* STEPPER CHAIN */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-6">
        {steps.map((step, idx) => {
          const isCompleted = step.status === 'COMPLETED';
          const isActive = step.status === 'ACTIVE';
          const isFailed = step.status === 'FAILED';
          const isSkipped = step.status === 'SKIPPED';

          return (
            <div key={step.stepId} className="relative flex items-start gap-4 font-mono">
              {/* VERTICAL LINE */}
              {idx < steps.length - 1 && (
                <div className={`absolute left-4 top-8 bottom-0 w-0.5 -ml-px ${
                  isCompleted ? 'bg-emerald-500/30' : isFailed ? 'bg-red-500/30' : 'bg-slate-800'
                }`} />
              )}

              {/* STEP NUMBER CIRCLE */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 z-10 border ${
                isCompleted ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 shadow-[0_0_10px_rgba(16,185,129,0.2)]' :
                isActive ? 'bg-blue-500/20 text-blue-400 border-blue-500/40 animate-pulse' :
                isFailed ? 'bg-red-500/20 text-red-400 border-red-500/40 shadow-[0_0_10px_rgba(239,68,68,0.2)]' :
                'bg-slate-950 text-slate-600 border-slate-800'
              }`}>
                {step.stepNumber}
              </div>

              {/* STEP CONTENT */}
              <div className="flex-1 pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-slate-100">{step.label}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded font-bold border ${
                      isCompleted ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                      isActive ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                      isFailed ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                      'bg-slate-950 text-slate-600 border-slate-800'
                    }`}>
                      {step.status}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-500">
                    {step.timestamp && <span>{step.timestamp}</span>}
                    {step.latencyMs !== undefined && step.latencyMs > 0 && (
                      <span className="ml-2 text-slate-400">+{step.latencyMs}ms</span>
                    )}
                  </div>
                </div>

                <p className="text-xs text-slate-400 mt-1">{step.description}</p>

                {step.detail && (
                  <div className="mt-2 p-2.5 rounded-xl bg-slate-950 border border-white/[0.06] text-xs text-slate-300 flex justify-between items-center">
                    <span>{step.detail}</span>
                    <span className="text-[10px] text-slate-500">ACTOR: {step.actor}</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
