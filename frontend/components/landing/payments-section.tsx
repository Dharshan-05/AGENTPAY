'use client';

import { CreditCard, Key, ShieldCheck, RefreshCw } from 'lucide-react';
import { Reveal } from '@/components/motion/reveal';
import { GlowCard } from '@/components/motion/glow-card';

export function PaymentsSection() {
  const CAPABILITIES = [
    {
      icon: CreditCard,
      title: 'Tokenized Virtual Cards',
      desc: 'Issue single-use or locked virtual card credentials per agent transaction with automatic expiration.',
    },
    {
      icon: Key,
      title: 'Cryptographic API Key Fingerprints',
      desc: 'Bind agent identities to public key infrastructure (PKI) ensuring non-repudiable financial intent.',
    },
    {
      icon: RefreshCw,
      title: 'Zero Recurring Risk',
      desc: 'Eliminate unauthorized subscription creep and unapproved vendor charges automatically.',
    },
  ];

  return (
    <section id="payments" className="py-24 px-6 relative">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Section Header */}
        <Reveal direction="up">
          <div className="text-center max-w-3xl mx-auto space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-mono font-bold uppercase tracking-wider">
              <CreditCard className="w-3.5 h-3.5" /> SECURE PAYMENT EXECUTION & RAILS
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-bold text-slate-100 tracking-tight">
              AGENT<span className="text-blue-400">PAYMENTS</span>
            </h2>
            <p className="text-slate-400 text-sm sm:text-base font-sans">
              Programmable financial rails, single-use tokenized cards, and zero-trust settlement infrastructure.
            </p>
          </div>
        </Reveal>

        {/* 3 Capabilities Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {CAPABILITIES.map((c, i) => {
            const Icon = c.icon;
            return (
              <Reveal key={c.title} direction="up" delay={i * 0.1}>
                <GlowCard className="p-6 h-full flex flex-col justify-between">
                  <div>
                    <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-4">
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-display font-bold text-lg text-slate-100 mb-2">{c.title}</h3>
                    <p className="text-xs font-mono text-slate-400 leading-relaxed">{c.desc}</p>
                  </div>
                  <div className="mt-6 pt-4 border-t border-white/[0.06] text-[10px] font-mono text-blue-400 font-bold uppercase flex items-center justify-between">
                    <span>ZERO-TRUST EXECUTION</span>
                    <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
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
