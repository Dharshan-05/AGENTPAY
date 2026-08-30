'use client';

import { LazyMotion, domAnimation, m, useMotionValue, useSpring } from 'framer-motion';
import { useEffect, useRef } from 'react';
import { SPRING } from '@/lib/motion';

interface Props {
  className?: string;
  colors?: string[];
  intensity?: number;
}

export function GradientMesh({
  className = '',
  colors = ['#10B981', '#3B82F6', '#6366F1'],
  intensity = 0.05,
}: Props) {
  const mouseX = useMotionValue(0.5);
  const mouseY = useMotionValue(0.5);
  const springX = useSpring(mouseX, SPRING.slow);
  const springY = useSpring(mouseY, SPRING.slow);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleMove(e: MouseEvent) {
      if (!ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      mouseX.set((e.clientX - rect.left) / rect.width);
      mouseY.set((e.clientY - rect.top) / rect.height);
    }
    window.addEventListener('mousemove', handleMove);
    return () => window.removeEventListener('mousemove', handleMove);
  }, [mouseX, mouseY]);

  const [c1, c2, c3] = colors;
  const hex = (c: string, a: number) => {
    const n = parseInt(c.replace('#', ''), 16);
    const r = (n >> 16) & 255;
    const g = (n >> 8) & 255;
    const b = n & 255;
    return `rgba(${r}, ${g}, ${b}, ${a})`;
  };

  return (
    <LazyMotion features={domAnimation}>
      <div ref={ref} className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`}>
        <m.div
          className="absolute inset-0 opacity-80"
          style={{
            background: `radial-gradient(ellipse 900px 700px at ${springX.get() * 100}% ${springY.get() * 100}%, ${hex(c1, intensity)}, transparent 60%)`,
          }}
        />
        <div
          className="absolute inset-0 opacity-70"
          style={{
            background: `radial-gradient(ellipse 1000px 800px at 85% 15%, ${hex(c2, intensity * 0.8)}, transparent 55%)`,
            animation: 'mesh-drift-a 22s ease-in-out infinite alternate',
          }}
        />
        <div
          className="absolute inset-0 opacity-60"
          style={{
            background: `radial-gradient(ellipse 800px 650px at 15% 85%, ${hex(c3, intensity * 0.7)}, transparent 55%)`,
            animation: 'mesh-drift-b 28s ease-in-out infinite alternate',
          }}
        />
        <div
          className="absolute inset-0 opacity-[0.02] mix-blend-overlay"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          }}
        />
        <style jsx>{`
          @keyframes mesh-drift-a {
            0% { transform: translate(0, 0); }
            100% { transform: translate(-30px, 20px); }
          }
          @keyframes mesh-drift-b {
            0% { transform: translate(0, 0); }
            100% { transform: translate(25px, -20px); }
          }
        `}</style>
      </div>
    </LazyMotion>
  );
}
