'use client';

import { Reveal } from '@/components/motion/reveal';
import { Magnetic } from '@/components/motion/magnetic';
import { ShimmerButton } from '@/components/motion/shimmer-button';
import { ShieldCheck, ArrowRight, BookOpen } from 'lucide-react';

export function FinalCta() {
  return (
    <section className="py-28 relative overflow-hidden">
      <div className="max-w-5xl mx-auto px-6 text-center">
        
        <Reveal y={12}>
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono uppercase tracking-widest mb-6">
            <ShieldCheck className="w-4 h-4" />
            Ready for Production Deployments
          </div>
        </Reveal>

        <Reveal y={16} delay={0.1}>
          <h2 className="text-4xl sm:text-6xl font-display font-bold text-slate-100 mb-6 tracking-tight">
            BUILD TRUSTED AGENTIC COMMERCE
          </h2>
        </Reveal>

        <Reveal y={16} delay={0.2}>
          <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto mb-10 font-sans leading-relaxed">
            Integrate AGENTPAY in under 10 minutes. Grant your AI agents programmable financial authorization with zero risk of unbudgeted spending.
          </p>
        </Reveal>

        <Reveal y={16} delay={0.3} className="flex flex-col sm:flex-row justify-center items-center gap-4">
          <Magnetic strength={14}>
            <ShimmerButton shimmerColor="rgba(16, 185, 129, 0.5)">
              <a
                href="#getstarted"
                className="inline-flex items-center gap-2.5 px-8 py-4 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 text-slate-950 font-bold text-sm uppercase tracking-wider font-mono shadow-[0_0_35px_rgba(16,185,129,0.35)] hover:shadow-[0_0_50px_rgba(16,185,129,0.5)] transition-all"
              >
                Start Building
                <ArrowRight className="w-4 h-4 text-slate-950" />
              </a>
            </ShimmerButton>
          </Magnetic>

          <Magnetic strength={14}>
            <a
              href="#docs"
              className="inline-flex items-center gap-2.5 px-8 py-4 rounded-xl bg-slate-900/80 border border-white/10 text-slate-200 font-semibold text-sm uppercase tracking-wider font-mono hover:bg-slate-800 hover:text-white hover:border-emerald-500/30 transition-all"
            >
              <BookOpen className="w-4 h-4 text-emerald-400" />
              Explore Documentation
            </a>
          </Magnetic>
        </Reveal>

      </div>
    </section>
  );
}
