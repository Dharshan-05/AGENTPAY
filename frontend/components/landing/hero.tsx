'use client';

import Link from 'next/link';
import { ArrowRight, ShieldCheck, Cpu, Lock, CheckCircle, Zap } from 'lucide-react';
import { SplitText } from '@/components/motion/split-text';
import { Reveal } from '@/components/motion/reveal';
import { ShimmerButton } from '@/components/motion/shimmer-button';
import { Magnetic } from '@/components/motion/magnetic';

export function Hero() {
  const STAGES = [
    { title: 'AGENT', desc: 'Autonomous AI Persona', icon: Cpu, color: 'text-blue-400', border: 'border-blue-500/30' },
    { title: 'INTENT', desc: 'Financial API Payload', icon: Zap, color: 'text-slate-300', border: 'border-slate-500/30' },
    { title: 'AGENTGUARD', desc: 'Policy & Spend Rules', icon: ShieldCheck, color: 'text-emerald-400', border: 'border-emerald-500/40' },
    { title: 'FRAUDGUARD', desc: 'AI Risk Intelligence', icon: Lock, color: 'text-amber-400', border: 'border-amber-500/30' },
    { title: 'DECISION', desc: 'Cryptographic Verdict', icon: CheckCircle, color: 'text-indigo-400', border: 'border-indigo-500/30' },
    { title: 'PAYMENT', desc: 'Tokenized Settlement', icon: ShieldCheck, color: 'text-emerald-400', border: 'border-emerald-400/50' },
  ];

  return (
    <section className="relative pt-36 pb-20 px-6 overflow-hidden">
      
      {/* Background Radial Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[350px] bg-emerald-500/10 blur-[120px] rounded-full pointer-events-none -z-10" />

      <div className="max-w-5xl mx-auto text-center space-y-8">
        
        {/* Category Pill */}
        <Reveal direction="down">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-semibold uppercase tracking-wider">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            ZERO-TRUST COMMERCE INFRASTRUCTURE FOR AI FLEETS
          </div>
        </Reveal>

        {/* Primary Message Title */}
        <Reveal direction="up" delay={0.1}>
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-display font-bold tracking-tight text-slate-100 leading-[1.08]">
            <SplitText text="THE TRUST LAYER FOR" mode="words" /> <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-blue-500 drop-shadow-[0_0_35px_rgba(16,185,129,0.35)]">
              AGENTIC COMMERCE
            </span>
          </h1>
        </Reveal>

        {/* Supporting Concept Subtitle */}
        <Reveal direction="up" delay={0.2}>
          <p className="max-w-2xl mx-auto text-slate-400 text-base sm:text-lg font-sans leading-relaxed">
            AI agents can act autonomously. <strong className="text-slate-200">AGENTPAY</strong> makes their financial actions{' '}
            <span className="text-emerald-400 font-mono">verifiable</span>,{' '}
            <span className="text-emerald-400 font-mono">policy-controlled</span>,{' '}
            <span className="text-emerald-400 font-mono">risk-aware</span>, and{' '}
            <span className="text-emerald-400 font-mono">explainable</span>.
          </p>
        </Reveal>

        {/* Primary Action Buttons */}
        <Reveal direction="up" delay={0.3}>
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link href="/command-center">
              <ShimmerButton className="px-8 py-3.5 rounded-xl font-mono font-bold text-slate-950 text-sm">
                Launch Command Center <ArrowRight className="w-4 h-4 ml-2 inline" />
              </ShimmerButton>
            </Link>

            <Magnetic>
              <Link href="#architecture">
                <button className="px-8 py-3.5 rounded-xl bg-slate-900/80 border border-white/10 hover:border-emerald-500/40 text-slate-200 hover:text-white font-mono font-semibold text-sm transition-all shadow-lg hover:shadow-emerald-500/10">
                  Explore Architecture
                </button>
              </Link>
            </Magnetic>
          </div>
        </Reveal>

        {/* AGENTPAY Financial Execution Flow Diagram */}
        <Reveal direction="up" delay={0.4}>
          <div className="pt-12">
            <div className="p-6 rounded-2xl bg-slate-950/80 border border-white/[0.08] backdrop-blur-xl shadow-2xl">
              <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] mb-6 font-mono text-xs text-slate-400">
                <span className="flex items-center gap-2 font-bold text-slate-200">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  AGENTPAY TRANSACTION PIPELINE
                </span>
                <span>REAL-TIME AUDIT LEDGER</span>
              </div>

              {/* Pipeline Nodes Flow */}
              <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                {STAGES.map((s, idx) => {
                  const Icon = s.icon;
                  return (
                    <div
                      key={s.title}
                      className={`p-3.5 rounded-xl bg-slate-900/60 border ${s.border} text-left transition-all hover:scale-[1.02]`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-mono text-slate-500 font-bold">0{idx + 1}</span>
                        <Icon className={`w-4 h-4 ${s.color}`} />
                      </div>
                      <h4 className={`font-mono font-bold text-xs ${s.color}`}>{s.title}</h4>
                      <p className="text-[10px] font-mono text-slate-400 mt-0.5 leading-tight">{s.desc}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </Reveal>

      </div>
    </section>
  );
}
