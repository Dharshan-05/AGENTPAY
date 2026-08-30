'use client';

import { LazyMotion, domAnimation, m } from 'framer-motion';
import { ReactNode } from 'react';

/**
 * MotionProvider — wraps children with Framer Motion's LazyMotion to optimize bundle size.
 */
export function MotionProvider({ children }: { children: ReactNode }) {
  return (
    <LazyMotion features={domAnimation} strict>
      {children}
    </LazyMotion>
  );
}

export { m };

/**
 * AGENTPAY Easing & Motion Presets — High precision spring physics and easing curves.
 */
export const EASE = {
  smooth: [0.22, 1, 0.36, 1] as [number, number, number, number],
  apple:  [0.16, 1, 0.3, 1] as [number, number, number, number],
  mat:    [0.4, 0, 0.2, 1] as [number, number, number, number],
  anti:   [0.83, 0, 0.17, 1] as [number, number, number, number],
} as const;

export const SPRING = {
  gentle:  { type: 'spring', stiffness: 120, damping: 20, mass: 1 } as const,
  snappy:  { type: 'spring', stiffness: 260, damping: 20, mass: 1 } as const,
  bouncy:  { type: 'spring', stiffness: 400, damping: 15, mass: 1 } as const,
  slow:    { type: 'spring', stiffness: 80, damping: 25, mass: 1 } as const,
} as const;

export const STAGGER = {
  fast:     { staggerChildren: 0.05, delayChildren: 0.1 },
  standard: { staggerChildren: 0.08, delayChildren: 0.15 },
  dramatic: { staggerChildren: 0.12, delayChildren: 0.25 },
} as const;

export const DURATION = {
  micro:     0.15,
  standard:  0.3,
  dramatic:  0.5,
  cinematic: 0.8,
} as const;

export const fadeInUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: DURATION.standard, ease: EASE.smooth } },
};

export const blurInFocus = {
  hidden: { opacity: 0, filter: 'blur(12px)' },
  visible: { opacity: 1, filter: 'blur(0px)', transition: { duration: DURATION.dramatic, ease: EASE.smooth } },
};

export const VIEWPORT = { once: true, margin: '-80px' } as const;
