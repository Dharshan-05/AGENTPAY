'use client';

import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  className?: string;
  shimmerColor?: string;
  duration?: number;
  disabled?: boolean;
}

export function ShimmerButton({
  children,
  className = '',
  shimmerColor = 'rgba(16, 185, 129, 0.4)',
  duration = 3,
  disabled = false,
}: Props) {
  if (disabled) return <>{children}</>;

  return (
    <div className={`relative inline-block overflow-hidden rounded-[inherit] ${className}`}>
      {children}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 rounded-[inherit]"
        style={{
          background: `linear-gradient(110deg, transparent 25%, ${shimmerColor} 50%, transparent 75%)`,
          backgroundSize: '200% 100%',
          animation: `shimmer-sweep ${duration}s ease-in-out infinite`,
          mixBlendMode: 'screen',
        }}
      />
      <style jsx>{`
        @keyframes shimmer-sweep {
          0%,
          40% {
            background-position: 200% 0;
          }
          60%,
          100% {
            background-position: -200% 0;
          }
        }
      `}</style>
    </div>
  );
}
