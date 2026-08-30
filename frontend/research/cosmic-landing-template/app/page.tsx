import { SplitText } from '@/components/motion/split-text';
import { LiquidGlass } from '@/components/motion/liquid-glass';
import { Magnetic } from '@/components/motion/magnetic';
import { Reveal, StaggerReveal } from '@/components/motion/reveal';
import { GradientMesh } from '@/components/motion/gradient-mesh';
import { NumberTicker } from '@/components/motion/number-ticker';
import { Marquee } from '@/components/motion/marquee';

const FEATURES = [
  { name: 'SplitText', desc: 'Character-by-character reveal with blur-to-focus.', color: '#00bcd4' },
  { name: 'LiquidGlass', desc: '4-layer glass with noise, sheen, tilt, and glow.', color: '#a78bfa' },
  { name: 'TiltCard', desc: '3D perspective tilt on hover via spring physics.', color: '#34d399' },
  { name: 'GlowCard', desc: 'Cursor-following border glow. Linear-tier.', color: '#60a5fa' },
  { name: 'Magnetic', desc: 'Cursor attraction on CTAs with spring physics.', color: '#f472b6' },
  { name: 'NumberTicker', desc: 'Count-up animation with spring interpolation.', color: '#fbbf24' },
];

const STATS = [
  { value: 12, suffix: '', label: 'Primitives' },
  { value: 0, suffix: '', label: 'Dependencies' },
  { value: 60, suffix: 'fps', label: 'Animations' },
];

const STACK = ['Next.js 16', 'React 19', 'Framer Motion 11', 'Tailwind CSS', 'TypeScript', 'MIT License'];

export default function Home() {
  return (
    <div className="relative min-h-screen">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-[#09090b]" />
        <GradientMesh colors={['#00bcd4', '#a78bfa', '#f472b6']} intensity={0.06} />
      </div>

      <main className="max-w-5xl mx-auto px-6">
        {/* Hero */}
        <section className="pt-32 pb-20 text-center">
          <Reveal y={12} blur>
            <p className="text-[11px] font-mono tracking-[0.3em] text-[#708094] mb-6 uppercase">
              12 motion primitives · MIT licensed · Copy and paste
            </p>
          </Reveal>

          <SplitText
            as="h1"
            text="Premium motion for Next.js."
            className="text-4xl md:text-6xl lg:text-7xl font-[family-name:var(--font-display)] font-bold text-[#e6eefc] mb-4 tracking-tight"
            delay={0.15}
            stagger={0.03}
          />

          <Reveal delay={0.8} y={12}>
            <p className="text-base md:text-lg text-[#9bb1d0] max-w-xl mx-auto leading-relaxed">
              LiquidGlass. SplitText. TiltCard. Magnetic. GlowCard. Marquee.
              Ship a premium dark landing page in minutes, not days.
            </p>
          </Reveal>

          <Reveal y={16} delay={1.0}>
            <div className="flex justify-center gap-10 mt-10">
              {STATS.map((s, i) => (
                <div key={s.label} className="text-center">
                  <p className="text-2xl md:text-3xl font-[family-name:var(--font-display)] font-bold text-[#e6eefc]">
                    <NumberTicker value={s.value} suffix={s.suffix} delay={1.2 + i * 0.1} />
                  </p>
                  <p className="text-[9px] font-mono tracking-widest uppercase text-[#708094] mt-1">{s.label}</p>
                </div>
              ))}
            </div>
          </Reveal>

          <Reveal y={12} delay={1.4}>
            <div className="flex justify-center gap-3 mt-10">
              <Magnetic>
                <a
                  href="https://github.com/frankxai/cosmic-landing-template"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#00bcd4]/10 border border-[#00bcd4]/30 text-sm font-medium text-[#00bcd4] hover:bg-[#00bcd4]/20 transition-all hover:shadow-[0_0_30px_rgba(0,188,212,0.15)]"
                >
                  View source
                </a>
              </Magnetic>
              <Magnetic>
                <a
                  href="https://vercel.com/new/clone?repository-url=https://github.com/frankxai/cosmic-landing-template"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white/[0.04] border border-white/[0.08] text-sm font-medium text-[#e6eefc] hover:bg-white/[0.08] transition-colors"
                >
                  Deploy to Vercel
                </a>
              </Magnetic>
            </div>
          </Reveal>
        </section>

        {/* Feature Grid */}
        <section className="mb-20">
          <Reveal y={12}>
            <p className="text-[10px] font-mono tracking-[0.25em] text-[#708094] mb-8 uppercase text-center">
              What&apos;s included
            </p>
          </Reveal>

          <StaggerReveal className="grid md:grid-cols-2 lg:grid-cols-3 gap-4" stagger={0.06}>
            {FEATURES.map((f) => (
              <Reveal key={f.name} y={20}>
                <LiquidGlass
                  intensity="standard"
                  tint={f.color}
                  glow
                  tilt
                  tiltIntensity={6}
                  className="rounded-2xl border border-white/[0.06] hover:border-white/[0.14] transition-colors"
                >
                  <div className="p-6">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: f.color, boxShadow: `0 0 12px ${f.color}60` }} />
                      <h3 className="text-sm font-[family-name:var(--font-display)] font-semibold text-[#e6eefc]">{f.name}</h3>
                    </div>
                    <p className="text-xs text-[#9bb1d0] leading-relaxed">{f.desc}</p>
                  </div>
                </LiquidGlass>
              </Reveal>
            ))}
          </StaggerReveal>
        </section>

        {/* Tech Stack Marquee */}
        <section className="mb-20">
          <Reveal y={12}>
            <p className="text-[10px] font-mono tracking-[0.25em] text-[#708094] mb-6 uppercase text-center">
              Built with
            </p>
          </Reveal>
          <Marquee duration={30}>
            {STACK.map((tech) => (
              <span
                key={tech}
                className="inline-flex items-center px-5 py-2 rounded-full bg-white/[0.03] border border-white/[0.06] text-xs font-mono text-white/50 whitespace-nowrap"
              >
                {tech}
              </span>
            ))}
          </Marquee>
        </section>

        {/* CTA */}
        <Reveal y={16} className="pb-24 text-center">
          <h2 className="text-2xl md:text-3xl font-[family-name:var(--font-display)] font-bold text-[#e6eefc] mb-3 tracking-tight">
            Your landing page. Your brand. Your code.
          </h2>
          <p className="text-sm text-[#9bb1d0] mb-6">
            MIT licensed. Copy the primitives into your project or deploy the whole template.
          </p>
          <Magnetic>
            <a
              href="https://vercel.com/new/clone?repository-url=https://github.com/frankxai/cosmic-landing-template"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-[#00bcd4] to-[#0d47a1] text-[#09090b] font-semibold text-sm hover:shadow-[0_0_40px_rgba(0,188,212,0.3)] transition-all"
            >
              Deploy now
            </a>
          </Magnetic>
        </Reveal>
      </main>
    </div>
  );
}
