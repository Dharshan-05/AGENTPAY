'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { Brain, Sparkles } from 'lucide-react';

export function AIInsights() {
  const insights = [
    'Transaction volume increased 18.6% during the selected period, driven primarily by infrastructure procurement.',
    'Procurement Agent #892 maintains the highest transaction success rate (97.8%) with zero critical risk violations.',
    'Velocity-related signals account for the largest share (35%) of high-risk anomaly detections across payment rails.',
    'Policy AGP-GOV-001 generated 34% of all governance interventions, successfully enforcing daily spend caps.',
  ];

  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-2 font-bold text-slate-100">
          <Brain className="w-4 h-4 text-purple-400" />
          <span className="text-sm">AI ANALYTICS INSIGHTS</span>
        </div>
        <AGBadge status="ACTIVE" label="AI-GENERATED DEMO INSIGHTS" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
        {insights.map((ins, idx) => (
          <div key={idx} className="p-3.5 rounded-xl bg-purple-500/10 border border-purple-500/30 space-y-1.5">
            <div className="flex items-center gap-1.5 text-purple-400 font-bold text-[10px]">
              <Sparkles className="w-3.5 h-3.5" />
              <span>INSIGHT #{idx + 1}</span>
            </div>
            <p className="text-slate-200 leading-relaxed">{ins}</p>
          </div>
        ))}
      </div>
    </AGCard>
  );
}
