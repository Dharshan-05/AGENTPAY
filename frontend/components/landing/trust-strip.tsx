'use client';

import { Marquee } from '@/components/motion/marquee';
import { Reveal } from '@/components/motion/reveal';
import { KeyRound, ShieldAlert, Cpu, Eye, CreditCard } from 'lucide-react';

const PILLARS = [
  { name: 'Identity', icon: KeyRound, desc: 'Cryptographic Agent IDs' },
  { name: 'Governance', icon: ShieldAlert, desc: 'AGENTGUARD Policies' },
  { name: 'Risk Intelligence', icon: Cpu, desc: 'FRAUDGUARD AI Detection' },
  { name: 'Explainability', icon: Eye, desc: 'Auditable Decision Trees' },
  { name: 'Payments', icon: CreditCard, desc: 'Atomic Settlement APIs' },
];

export function TrustStrip() {
  return (
    <section className="py-12 border-y border-white/[0.06] bg-slate-950/40 relative">
      <div className="max-w-7xl mx-auto px-6 mb-6 text-center">
        <Reveal y={10}>
          <p className="text-[11px] font-mono tracking-[0.25em] text-slate-500 uppercase">
            Core Foundations of Verifiable Autonomous Commerce
          </p>
        </Reveal>
      </div>

      <Marquee duration={30} pauseOnHover={true}>
        {PILLARS.map((p) => {
          const Icon = p.icon;
          return (
            <div
              key={p.name}
              className="flex items-center gap-3 px-6 py-3 rounded-xl bg-slate-900/60 border border-white/[0.08] hover:border-emerald-500/40 transition-colors group cursor-default"
            >
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Icon className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="flex flex-col text-left">
                <span className="text-xs font-mono font-bold text-slate-200 tracking-wider uppercase">
                  {p.name}
                </span>
                <span className="text-[10px] font-sans text-slate-400">
                  {p.desc}
                </span>
              </div>
            </div>
          );
        })}
      </Marquee>
    </section>
  );
}
