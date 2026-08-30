'use client';

import { ShieldCheck, Lock, FileKey, Award } from 'lucide-react';
import { Reveal } from '@/components/motion/reveal';
import { GlowCard } from '@/components/motion/glow-card';

export function SecurityTrust() {
  const BADGES = [
    {
      icon: ShieldCheck,
      title: 'SOC 2 Type II Certified',
      desc: 'Enterprise-grade security controls for financial data and agent execution logs.',
    },
    {
      icon: Lock,
      title: 'Zero-Trust Encryption',
      desc: 'End-to-end AES-256 and TLS 1.3 cryptographic payload signing across all rails.',
    },
    {
      icon: FileKey,
      title: 'PKI Key Pair Hardware Binding',
      desc: 'Hardware security modules (HSM) store private keys isolated from autonomous LLMs.',
    },
    {
      icon: Award,
      title: '100% Audit Compliance',
      desc: 'Non-repudiable transaction ledgers with real-time SecOps export capabilities.',
    },
  ];

  return (
    <section id="security" className="py-24 px-6 relative bg-slate-950/40 border-y border-white/[0.06]">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Section Header */}
        <Reveal direction="up">
          <div className="text-center max-w-3xl mx-auto space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold uppercase tracking-wider">
              <ShieldCheck className="w-3.5 h-3.5" /> CRYPTOGRAPHIC TRUST & COMPLIANCE
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-bold text-slate-100 tracking-tight">
              BUILT FOR ENTERPRISE SECURITY
            </h2>
            <p className="text-slate-400 text-sm sm:text-base font-sans">
              Zero-trust architecture designed to satisfy banking compliance, CISO governance, and financial audits.
            </p>
          </div>
        </Reveal>

        {/* 4 Trust Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {BADGES.map((b, i) => {
            const Icon = b.icon;
            return (
              <Reveal key={b.title} direction="up" delay={i * 0.1}>
                <GlowCard className="p-6 h-full flex flex-col justify-between">
                  <div>
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4">
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-display font-bold text-base text-slate-100 mb-2">{b.title}</h3>
                    <p className="text-xs font-mono text-slate-400 leading-relaxed">{b.desc}</p>
                  </div>
                  <div className="mt-6 pt-4 border-t border-white/[0.06] text-[10px] font-mono text-emerald-400 font-bold uppercase flex items-center justify-between">
                    <span>VERIFIED STANDARD</span>
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
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
