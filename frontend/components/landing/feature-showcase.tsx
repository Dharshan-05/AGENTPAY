'use client';

import { Reveal, StaggerReveal } from '@/components/motion/reveal';
import { GlowCard } from '@/components/motion/glow-card';
import { Bot, ShieldCheck, Cpu, Eye, UserCheck, FileCheck } from 'lucide-react';

const FEATURES = [
  {
    title: 'Autonomous Agent Payments',
    icon: Bot,
    color: '#3B82F6',
    desc: 'Empower AI agents with direct API payment execution capabilities bound strictly to authenticated agent sessions.',
  },
  {
    title: 'Policy-Controlled Commerce',
    icon: ShieldCheck,
    color: '#10B981',
    desc: 'Set hard spending limits, vendor whitelists, allowed merchant categories, and time windows with AGENTGUARD.',
  },
  {
    title: 'Real-Time Fraud Detection',
    icon: Cpu,
    color: '#6366F1',
    desc: 'FRAUDGUARD scans every intent payload in under 20ms for prompt injections, hallucination loops, and financial anomalies.',
  },
  {
    title: 'Explainable Decisions',
    icon: Eye,
    color: '#60A5FA',
    desc: 'Every approval or rejection includes human-readable reasoning and transparent risk factor score breakdowns.',
  },
  {
    title: 'Human-in-the-Loop Approval',
    icon: UserCheck,
    color: '#F59E0B',
    desc: 'Seamless human escalation for high-value or out-of-policy requests with one-click Slack, email, or webhook authorizations.',
  },
  {
    title: 'Complete Auditability',
    icon: FileCheck,
    color: '#34D399',
    desc: 'Cryptographic ledger logging every prompt context, decision policy, risk score, and transaction receipt for compliance.',
  },
];

export function FeatureShowcase() {
  return (
    <section className="py-24 relative bg-slate-950/40 border-t border-white/[0.06]">
      <div className="max-w-7xl mx-auto px-6">
        
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Reveal y={12}>
            <p className="text-[11px] font-mono tracking-[0.25em] text-emerald-400 uppercase mb-3">
              Platform Capabilities
            </p>
          </Reveal>
          <Reveal y={16} delay={0.1}>
            <h2 className="text-3xl sm:text-5xl font-display font-bold text-slate-100 mb-6 tracking-tight">
              FEATURE SHOWCASE
            </h2>
          </Reveal>
          <Reveal y={16} delay={0.2}>
            <p className="text-base text-slate-400 font-sans">
              Purpose-built infrastructure for secure, programmable, enterprise agent financial ops.
            </p>
          </Reveal>
        </div>

        <StaggerReveal className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" stagger={0.06}>
          {FEATURES.map((f) => {
            const Icon = f.icon;
            return (
              <Reveal key={f.title} y={20}>
                <GlowCard
                  color={f.color}
                  className="rounded-2xl bg-slate-900/40 border border-white/[0.08] hover:border-white/20 transition-all h-full p-6"
                >
                  <div className="flex flex-col justify-between h-full">
                    <div>
                      <div
                        className="w-10 h-10 rounded-xl flex items-center justify-center border mb-5"
                        style={{
                          backgroundColor: `${f.color}15`,
                          borderColor: `${f.color}30`,
                          color: f.color,
                        }}
                      >
                        <Icon className="w-5 h-5" />
                      </div>
                      <h3 className="text-lg font-display font-bold text-slate-100 mb-2">
                        {f.title}
                      </h3>
                      <p className="text-xs text-slate-400 font-sans leading-relaxed">
                        {f.desc}
                      </p>
                    </div>

                    <div className="mt-6 pt-4 border-t border-white/[0.06] flex items-center justify-between text-[10px] font-mono text-slate-500">
                      <span>ENTERPRISE READY</span>
                      <span style={{ color: f.color }}>MODULE READY</span>
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
