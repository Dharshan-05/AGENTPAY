'use client';

import { Reveal, StaggerReveal } from '@/components/motion/reveal';
import { GlowCard } from '@/components/motion/glow-card';
import { Fingerprint, Scroll, AlertTriangle, Scale, ShieldAlert } from 'lucide-react';

const REQUIREMENTS = [
  {
    title: 'Identity',
    icon: Fingerprint,
    desc: 'Unforgeable cryptographic identification for every AI agent initiating financial requests.',
    stat: 'Zero-Trust ID',
  },
  {
    title: 'Policy',
    icon: Scroll,
    desc: 'Real-time deterministic enforcement of budgets, vendor limits, and business spending rules.',
    stat: '100% Policy Bound',
  },
  {
    title: 'Risk',
    icon: AlertTriangle,
    desc: 'Deep AI context analysis detecting malicious prompt injections, rogue loops, and anomalous transactions.',
    stat: 'Sub-20ms Scoring',
  },
  {
    title: 'Accountability',
    icon: Scale,
    desc: 'Immutable audit logs with human-in-the-loop escalation paths for edge case approvals.',
    stat: 'Verifiable Ledger',
  },
];

export function Problem() {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-6">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Reveal y={12}>
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-mono uppercase tracking-widest mb-4">
              <ShieldAlert className="w-3.5 h-3.5" />
              The Financial Autonomy Gap
            </div>
          </Reveal>

          <Reveal y={16} delay={0.1}>
            <h2 className="text-3xl sm:text-5xl font-display font-bold text-slate-100 mb-6 tracking-tight">
              Autonomous agents are becoming capable of making real-world decisions.
            </h2>
          </Reveal>

          <Reveal y={16} delay={0.2}>
            <p className="text-base sm:text-lg text-slate-400 font-sans leading-relaxed">
              Without dedicated financial security infrastructure, granting AI agents payment authority leads to unbounded risk, unauthorized vendor spend, and zero accountability.
            </p>
          </Reveal>
        </div>

        {/* 4 Pillars of Financial Autonomy */}
        <StaggerReveal className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" stagger={0.08}>
          {REQUIREMENTS.map((item) => {
            const Icon = item.icon;
            return (
              <Reveal key={item.title} y={20}>
                <GlowCard color="#10B981" className="h-full rounded-2xl bg-slate-900/50 border border-white/[0.08] p-6 hover:border-emerald-500/40 transition-colors">
                  <div className="flex flex-col h-full justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                          <Icon className="w-5 h-5 text-emerald-400" />
                        </div>
                        <span className="text-[10px] font-mono tracking-wider text-emerald-400 uppercase bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                          {item.stat}
                        </span>
                      </div>
                      <h3 className="text-xl font-display font-bold text-slate-100 mb-2">
                        {item.title}
                      </h3>
                      <p className="text-xs text-slate-400 leading-relaxed font-sans">
                        {item.desc}
                      </p>
                    </div>
                    <div className="mt-6 pt-4 border-t border-white/[0.06] flex items-center gap-2 text-[10px] font-mono text-slate-500">
                      <span>AGENTPAY MANDATE</span>
                    </div>
                  </div>
                </GlowCard>
              </Reveal>
            );
          })}
        </StaggerReveal>

      </div>
    </section>
  );
}
