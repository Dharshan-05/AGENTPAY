'use client';

import { useEffect, useState } from 'react';
import { LazyMotion, domAnimation, m, useMotionValue, useSpring } from 'framer-motion';
import { SPRING } from '@/lib/motion';

interface Props {
  hoverSelector?: string;
}

export function CursorFollower({ hoverSelector = 'a, button, [role="button"]' }: Props) {
  const [enabled, setEnabled] = useState(false);
  const [hovering, setHovering] = useState(false);
  const [visible, setVisible] = useState(false);

  const x = useMotionValue(-100);
  const y = useMotionValue(-100);
  const springX = useSpring(x, { stiffness: 500, damping: 30, mass: 0.5 });
  const springY = useSpring(y, { stiffness: 500, damping: 30, mass: 0.5 });

  useEffect(() => {
    const mq = window.matchMedia('(pointer: fine)');
    if (!mq.matches) return;
    setEnabled(true);

    function handleMove(e: MouseEvent) {
      x.set(e.clientX);
      y.set(e.clientY);
      if (!visible) setVisible(true);
    }

    function handleLeave() {
      setVisible(false);
    }

    function handleOver(e: MouseEvent) {
      const target = e.target as HTMLElement;
      if (target?.matches?.(hoverSelector) || target?.closest?.(hoverSelector)) {
        setHovering(true);
      } else {
        setHovering(false);
      }
    }

    window.addEventListener('mousemove', handleMove);
    document.addEventListener('mouseleave', handleLeave);
    document.addEventListener('mouseover', handleOver);

    return () => {
      window.removeEventListener('mousemove', handleMove);
      document.removeEventListener('mouseleave', handleLeave);
      document.removeEventListener('mouseover', handleOver);
    };
  }, [hoverSelector, x, y, visible]);

  if (!enabled) return null;

  return (
    <LazyMotion features={domAnimation}>
      <m.div
        className="pointer-events-none fixed z-[9999] rounded-full border border-emerald-500/30 mix-blend-screen"
        style={{
          x: springX,
          y: springY,
          translateX: '-50%',
          translateY: '-50%',
        }}
        animate={{
          width: hovering ? 44 : 26,
          height: hovering ? 44 : 26,
          opacity: visible ? 1 : 0,
          borderColor: hovering ? 'rgba(16,185,129,0.5)' : 'rgba(255,255,255,0.15)',
        }}
        transition={SPRING.snappy}
      />
      <m.div
        className="pointer-events-none fixed z-[9999] rounded-full bg-emerald-400 mix-blend-screen"
        style={{
          x,
          y,
          translateX: '-50%',
          translateY: '-50%',
        }}
        animate={{
          width: hovering ? 0 : 4,
          height: hovering ? 0 : 4,
          opacity: visible && !hovering ? 1 : 0,
        }}
        transition={SPRING.bouncy}
      />
    </LazyMotion>
  );
}
