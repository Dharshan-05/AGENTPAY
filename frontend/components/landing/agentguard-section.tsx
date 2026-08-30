'use client';

import { Shield, Sliders, Lock, FileCheck, CheckCircle2 } from 'lucide-react';
import { Reveal } from '@/components/motion/reveal';
import { GlowCard } from '@/components/motion/glow-card';

export function AgentGuardSection() {
  const FEATURES = [
    {
      icon: Sliders,
      title: 'Dynamic Spend Velocities',
      desc: 'Set hard caps per transaction, per day, or per vendor. Automatically throttle agents approaching budget limits.',
    },
    {
      icon: Lock,
      title: 'Merchant & API Whitelisting',
      desc: 'Restrict agents to pre-approved merchant Category Codes (MCCs), domain patterns, and vendor endpoints.',
    },
    {
      icon: FileCheck,
      title: 'Cryptographic Policy Rules',
      desc: 'Policies are compiled into zero-trust rules signed with public key fingerprints for tamper-proof execution.',
    },
    {
      icon: CheckCircle2,
      title: 'Human-in-the-Loop Escalation',
      desc: 'Transactions exceeding autonomous thresholds automatically route to SecOps admins for one-click approval.',
    },
  ];

  return (
    <section id="agentguard" className="py-24 px-6 relative">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Section Header */}
        <Reveal direction="up">
          <div className="text-center max-w-3xl mx-auto space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold uppercase tracking-wider">
              <Shield className="w-3.5 h-3.5" /> POLICY & GOVERNANCE ENGINE
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-bold text-slate-100 tracking-tight">
              AGENT<span className="text-emerald-400">GUARD</span>
            </h2>
            <p className="text-slate-400 text-sm sm:text-base font-sans">
              Autonomous financial permissions, role-based authorization, and spend policy governance for AI agent fleets.
            </p>
          </div>
        </Reveal>

        {/* 4 Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {FEATURES.map((f, i) => {
            const Icon = f.icon;
            return (
              <Reveal key={f.title} direction="up" delay={i * 0.1}>
                <GlowCard className="p-6 h-full flex flex-col justify-between">
                  <div>
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4">
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-display font-bold text-lg text-slate-100 mb-2">{f.title}</h3>
                    <p className="text-xs font-mono text-slate-400 leading-relaxed">{f.desc}</p>
                  </div>
                  <div className="mt-6 pt-4 border-t border-white/[0.06] text-[10px] font-mono text-emerald-400 font-bold uppercase flex items-center justify-between">
                    <span>AGENTGUARD ENGINE</span>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  </div>
                </GlowCard>
              </Reveal>
            );
          })}
        </div>

      </div>
    </section>
  );
}
