'use client';

import { Reveal, StaggerReveal } from '@/components/motion/reveal';
import { LiquidGlass } from '@/components/motion/liquid-glass';
import { ShieldCheck, Lock, Cpu, CreditCard, ArrowUpRight } from 'lucide-react';

const MODEL_PILLARS = [
  {
    name: 'AGENTPAY',
    role: 'Agent Identity + Execution',
    icon: ShieldCheck,
    color: '#3B82F6',
    items: [
      'Cryptographic Agent Passports',
      'API key & Session delegation',
      'Scoped wallet isolation',
    ],
    desc: 'Binds agent identities directly to verified cryptographic credentials with fine-grained capability tokens.',
  },
  {
    name: 'AGENTGUARD',
    role: 'Policy + Authorization + Governance',
    icon: Lock,
    color: '#10B981',
    items: [
      'Deterministic spend limits',
      'Merchant & Category whitelists',
      'Time-locked authorization windows',
    ],
    desc: 'The programmable policy engine enforcing organizational rules before any money moves.',
  },
  {
    name: 'FRAUDGUARD',
    role: 'Risk Detection + Explainability',
    icon: Cpu,
    color: '#6366F1',
    items: [
      'Prompt injection defense',
      'Anomalous velocity checks',
      'Natural language audit trees',
    ],
    desc: 'AI-native real-time risk intelligence analyzing agent intent against baseline behavioural vectors.',
  },
  {
    name: 'PAYMENTS',
    role: 'Secure Financial Execution',
    icon: CreditCard,
    color: '#34D399',
    items: [
      'Atomic virtual card generation',
      'Real-time ACH & FedNow rails',
      'Instant Webhooks & Reconciliations',
    ],
    desc: 'Bank-grade multi-rail payment engine built specifically for programmatic API-driven disbursements.',
  },
];

export function Architecture() {
  return (
    <section className="py-24 relative bg-slate-950/60 border-y border-white/[0.06]">
      <div className="max-w-7xl mx-auto px-6">
        
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Reveal y={12}>
            <p className="text-[11px] font-mono tracking-[0.25em] text-emerald-400 uppercase mb-3">
              Architectural Breakdown
            </p>
          </Reveal>
          <Reveal y={16} delay={0.1}>
            <h2 className="text-3xl sm:text-5xl font-display font-bold text-slate-100 mb-6 tracking-tight">
              THE AGENTPAY MODEL
            </h2>
          </Reveal>
          <Reveal y={16} delay={0.2}>
            <p className="text-base text-slate-400 font-sans">
              Four unified technology layers powering verifiable, risk-controlled financial autonomy.
            </p>
          </Reveal>
        </div>

        <StaggerReveal className="grid grid-cols-1 md:grid-cols-2 gap-8" stagger={0.08}>
          {MODEL_PILLARS.map((pillar) => {
            const Icon = pillar.icon;
            return (
              <Reveal key={pillar.name} y={24}>
                <LiquidGlass
                  intensity="standard"
                  tint={pillar.color}
                  glow
                  tilt
                  tiltIntensity={4}
                  className="rounded-2xl border border-white/[0.08] hover:border-white/[0.18] transition-colors h-full"
                >
                  <div className="p-8 flex flex-col justify-between h-full">
                    <div>
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-12 h-12 rounded-xl flex items-center justify-center border"
                            style={{
                              backgroundColor: `${pillar.color}15`,
                              borderColor: `${pillar.color}40`,
                              color: pillar.color,
                            }}
                          >
                            <Icon className="w-6 h-6" />
                          </div>
                          <div>
                            <h3 className="text-2xl font-display font-bold text-slate-100 tracking-tight">
                              {pillar.name}
                            </h3>
                            <span className="text-xs font-mono text-slate-400">
                              {pillar.role}
                            </span>
                          </div>
                        </div>
                        <ArrowUpRight className="w-5 h-5 text-slate-500 group-hover:text-slate-200 transition-colors" />
                      </div>

                      <p className="text-sm text-slate-300 mb-6 leading-relaxed font-sans">
                        {pillar.desc}
                      </p>

                      <ul className="space-y-2.5 mb-6 border-t border-white/[0.06] pt-6">
                        {pillar.items.map((item) => (
                          <li key={item} className="flex items-center gap-2.5 text-xs font-mono text-slate-400">
                            <span
                              className="w-1.5 h-1.5 rounded-full"
                              style={{ backgroundColor: pillar.color }}
                            />
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-500">
                      <span>MODULE ID: {pillar.name}_v1</span>
                      <span className="text-emerald-400">STATUS: ACTIVE</span>
                    </div>
                  </div>
                </LiquidGlass>
              </Reveal>
            );
          })}
        </StaggerReveal>

      </div>
    </section>
  );
}
