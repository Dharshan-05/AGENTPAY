'use client';

import { LazyMotion, domAnimation, m, type Variants } from 'framer-motion';
import { EASE, VIEWPORT } from '@/lib/motion';

interface Props {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  y?: number;
  blur?: boolean;
  direction?: 'up' | 'down' | 'left' | 'right';
  as?: 'div' | 'section' | 'article' | 'span';
}

export function Reveal({ children, className = '', delay = 0, y = 20, blur = true, direction = 'up', as = 'div' }: Props) {
  const initialY = direction === 'down' ? -y : direction === 'up' ? y : 0;
  const variants: Variants = {
    hidden: {
      opacity: 0,
      y: initialY,
      filter: blur ? 'blur(10px)' : 'blur(0px)',
    },
    visible: {
      opacity: 1,
      y: 0,
      filter: 'blur(0px)',
      transition: { duration: 0.6, ease: EASE.smooth, delay },
    },
  };

  const Component = as === 'section' ? m.section : as === 'article' ? m.article : as === 'span' ? m.span : m.div;

  return (
    <LazyMotion features={domAnimation}>
      <Component
        className={className}
        initial="hidden"
        whileInView="visible"
        viewport={VIEWPORT}
        variants={variants}
      >
        {children}
      </Component>
    </LazyMotion>
  );
}

export function StaggerReveal({ children, className = '', stagger = 0.08, delay = 0.15 }: {
  children: React.ReactNode;
  className?: string;
  stagger?: number;
  delay?: number;
}) {
  const variants: Variants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: stagger,
        delayChildren: delay,
      },
    },
  };

  return (
    <LazyMotion features={domAnimation}>
      <m.div
        className={className}
        initial="hidden"
        whileInView="visible"
        viewport={VIEWPORT}
        variants={variants}
      >
        {children}
      </m.div>
    </LazyMotion>
  );
}
