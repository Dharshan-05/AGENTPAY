'use client';

import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  direction?: 'left' | 'right';
  duration?: number;
  pauseOnHover?: boolean;
  fade?: boolean;
  className?: string;
}

export function Marquee({
  children,
  direction = 'left',
  duration = 35,
  pauseOnHover = true,
  fade = true,
  className = '',
}: Props) {
  const animationName = direction === 'left' ? 'marquee-left' : 'marquee-right';

  return (
    <div
      className={`group relative flex overflow-hidden ${className}`}
      style={{
        maskImage: fade
          ? 'linear-gradient(to right, transparent, black 12%, black 88%, transparent)'
          : undefined,
        WebkitMaskImage: fade
          ? 'linear-gradient(to right, transparent, black 12%, black 88%, transparent)'
          : undefined,
      }}
    >
      <div
        className="flex shrink-0 gap-8 pr-8"
        style={{
          animation: `${animationName} ${duration}s linear infinite`,
          animationPlayState: 'running',
        }}
        onMouseEnter={(e) => {
          if (pauseOnHover) e.currentTarget.style.animationPlayState = 'paused';
        }}
        onMouseLeave={(e) => {
          if (pauseOnHover) e.currentTarget.style.animationPlayState = 'running';
        }}
      >
        {children}
      </div>
      <div
        aria-hidden
        className="flex shrink-0 gap-8 pr-8"
        style={{
          animation: `${animationName} ${duration}s linear infinite`,
          animationPlayState: 'running',
        }}
      >
        {children}
      </div>
      <style jsx>{`
        @keyframes marquee-left {
          from {
            transform: translateX(0);
          }
          to {
            transform: translateX(-100%);
          }
        }
        @keyframes marquee-right {
          from {
            transform: translateX(-100%);
          }
          to {
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
}
