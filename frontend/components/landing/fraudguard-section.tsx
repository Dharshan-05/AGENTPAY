'use client';

import { Cpu, AlertTriangle, Eye, ShieldAlert, Zap } from 'lucide-react';
import { Reveal } from '@/components/motion/reveal';
import { GlowCard } from '@/components/motion/glow-card';

export function FraudGuardSection() {
  const INSIGHTS = [
    {
      title: 'Prompt Injection Defense',
      desc: 'Detects adversarial prompt instructions attempting to hijack agent payment instructions or bypass budget limits.',
      riskScore: 0.92,
      status: 'BLOCKED',
    },
    {
      title: 'Spend Velocity Spike Detection',
      desc: 'Real-time anomaly detection flags rapid bursts of high-frequency transactions before settlement.',
      riskScore: 0.78,
      status: 'REVIEW',
    },
    {
      title: 'Explainable AI Risk Scoring',
      desc: 'Every financial verdict includes clear human-readable rationales and confidence intervals.',
      riskScore: 0.04,
      status: 'AUTHORIZED',
    },
  ];

  return (
    <section id="fraudguard" className="py-24 px-6 relative bg-slate-950/40 border-y border-white/[0.06]">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Section Header */}
        <Reveal direction="up">
          <div className="text-center max-w-3xl mx-auto space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono font-bold uppercase tracking-wider">
              <Cpu className="w-3.5 h-3.5" /> AI RISK INTEL & ANOMALY DETECTION
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-bold text-slate-100 tracking-tight">
              FRAUD<span className="text-amber-400">GUARD</span>
            </h2>
            <p className="text-slate-400 text-sm sm:text-base font-sans">
              Real-time AI fraud detection, adversarial prompt injection defense, and explainable risk intelligence.
            </p>
          </div>
        </Reveal>

        {/* Risk Intelligence Demo Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {INSIGHTS.map((item, i) => (
            <Reveal key={item.title} direction="up" delay={i * 0.1}>
              <GlowCard className="p-6 h-full flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span
                      className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold uppercase border ${
                        item.status === 'BLOCKED'
                          ? 'bg-red-500/10 text-red-400 border-red-500/30'
                          : item.status === 'REVIEW'
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      }`}
                    >
                      {item.status}
                    </span>
                    <span className="font-mono text-xs text-slate-400">
                      Risk: <strong className="text-slate-100">{item.riskScore}</strong>
                    </span>
                  </div>

                  <h3 className="font-display font-bold text-lg text-slate-100 mb-2">{item.title}</h3>
                  <p className="text-xs font-mono text-slate-400 leading-relaxed">{item.desc}</p>
                </div>

                <div className="mt-6 pt-4 border-t border-white/[0.06] flex items-center justify-between text-[10px] font-mono text-slate-500">
                  <span className="flex items-center gap-1">
                    <Eye className="w-3 h-3 text-slate-400" /> Explainable AI Model
                  </span>
                  <span className="text-amber-400 font-bold">100% Inspected</span>
                </div>
              </GlowCard>
            </Reveal>
          ))}
        </div>

      </div>
    </section>
  );
}
