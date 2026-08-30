'use client';

import { Cpu, AlertTriangle, ShieldCheck, Zap, ArrowRight, Info } from 'lucide-react';

export interface InsightItem {
  id: string;
  type: 'WARNING' | 'OPTIMIZATION' | 'SECURITY_ALERT';
  title: string;
  desc: string;
  recommendation: string;
  targetAgent: string;
  savingsOrRisk: string;
}

interface RiskInsightsProps {
  insights: InsightItem[];
  onApplyRecommendation: (id: string) => void;
}

export function RiskInsights({ insights, onApplyRecommendation }: RiskInsightsProps) {
  return (
    <div className="bg-slate-950/80 border border-white/[0.08] rounded-2xl p-6 backdrop-blur-xl h-full flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] mb-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-display font-bold text-base text-slate-100 tracking-tight">
                AI OPERATIONAL INSIGHTS
              </h3>
              <span className="text-[10px] font-mono text-slate-400">
                FRAUDGUARD Contextual Security & Optimization Engine
              </span>
            </div>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 uppercase">
            3 Active Scans
          </span>
        </div>

        <div className="space-y-4">
          {insights.map((item) => {
            const isAlert = item.type === 'SECURITY_ALERT';
            const isWarning = item.type === 'WARNING';

            return (
              <div
                key={item.id}
                className={`p-4 rounded-xl border transition-all ${
                  isAlert
                    ? 'bg-red-500/5 border-red-500/30 hover:border-red-500/50'
                    : isWarning
                    ? 'bg-amber-500/5 border-amber-500/30 hover:border-amber-500/50'
                    : 'bg-indigo-500/5 border-indigo-500/30 hover:border-indigo-500/50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {isAlert ? (
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                    ) : isWarning ? (
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                    ) : (
                      <Zap className="w-4 h-4 text-indigo-400" />
                    )}
                    <span className="text-xs font-mono font-bold text-slate-200">
                      {item.title}
                    </span>
                  </div>
                  <span className="text-[9px] font-mono text-slate-400 uppercase">
                    {item.targetAgent}
                  </span>
                </div>

                <p className="text-xs font-sans text-slate-400 mb-3 leading-relaxed">
                  {item.desc}
                </p>

                <div className="flex items-center justify-between pt-3 border-t border-white/[0.06] text-[10px] font-mono">
                  <span className="text-slate-300">
                    Impact: <strong className={isAlert ? 'text-red-400' : 'text-emerald-400'}>{item.savingsOrRisk}</strong>
                  </span>
                  <button
                    onClick={() => onApplyRecommendation(item.id)}
                    className="inline-flex items-center gap-1 text-emerald-400 hover:underline font-bold"
                  >
                    Apply Guard Policy <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="pt-3 border-t border-white/[0.06] flex items-center justify-between text-[10px] font-mono text-slate-500">
        <span>MODEL: FRAUDGUARD-v4.2</span>
        <span className="text-emerald-400">ENFORCING ZERO-TRUST</span>
      </div>
    </div>
  );
}
