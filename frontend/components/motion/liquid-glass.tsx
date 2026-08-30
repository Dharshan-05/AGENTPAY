'use client';

import * as React from 'react';

interface LiquidGlassProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  intensity?: 'subtle' | 'standard' | 'heavy';
  tint?: string;
  glow?: boolean;
  sheen?: boolean;
  noise?: boolean;
  tilt?: boolean;
  tiltIntensity?: number;
}

const INTENSITY_MAP = {
  subtle:   { blur: '12px', sat: '130%', bg: 'rgba(11, 15, 23, 0.4)' },
  standard: { blur: '20px', sat: '150%', bg: 'rgba(14, 19, 31, 0.6)' },
  heavy:    { blur: '32px', sat: '180%', bg: 'rgba(20, 26, 41, 0.75)' },
} as const;

const LiquidGlass = React.forwardRef<HTMLDivElement, LiquidGlassProps>(
  (
    {
      children,
      className = '',
      intensity = 'standard',
      tint = '#10B981',
      glow = false,
      sheen = true,
      noise = true,
      tilt = false,
      tiltIntensity = 6,
      style,
      ...props
    },
    ref,
  ) => {
    const innerRef = React.useRef<HTMLDivElement>(null);
    const [pos, setPos] = React.useState({ x: -9999, y: -9999 });
    const [hovering, setHovering] = React.useState(false);
    const [transform, setTransform] = React.useState({ rotateX: 0, rotateY: 0 });
    const cfg = INTENSITY_MAP[intensity];

    const glowRgba = React.useMemo(() => {
      const cleanHex = tint.replace('#', '');
      const n = parseInt(cleanHex.length === 3 ? cleanHex.split('').map(c => c + c).join('') : cleanHex, 16);
      if (isNaN(n)) return '16, 185, 129';
      const r = (n >> 16) & 255;
      const g = (n >> 8) & 255;
      const b = n & 255;
      return `${r}, ${g}, ${b}`;
    }, [tint]);

    function handleMove(e: React.MouseEvent<HTMLDivElement>) {
      const el = innerRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      if (sheen) setPos({ x, y });

      if (tilt) {
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        setTransform({
          rotateX: ((y - centerY) / centerY) * -tiltIntensity,
          rotateY: ((x - centerX) / centerX) * tiltIntensity,
        });
      }
    }

    function handleLeave() {
      setHovering(false);
      setPos({ x: -9999, y: -9999 });
      if (tilt) setTransform({ rotateX: 0, rotateY: 0 });
    }

    return (
      <div
        ref={ref}
        className={`relative ${className}`}
        style={{ perspective: tilt ? '1000px' : undefined, ...style }}
        {...props}
      >
        {glow && (
          <div
            className="absolute -inset-2 rounded-[inherit] blur-xl transition-opacity duration-300 pointer-events-none"
            style={{
              background: `linear-gradient(135deg, rgba(${glowRgba}, 0.25), rgba(${glowRgba}, 0.08))`,
              opacity: hovering ? 0.8 : 0.2,
            }}
          />
        )}

        <div
          ref={innerRef}
          onMouseMove={handleMove}
          onMouseEnter={() => setHovering(true)}
          onMouseLeave={handleLeave}
          className="relative overflow-hidden rounded-[inherit] isolate h-full"
          style={{
            backgroundColor: cfg.bg,
            backdropFilter: `blur(${cfg.blur}) saturate(${cfg.sat}) brightness(${hovering ? 1.04 : 1})`,
            WebkitBackdropFilter: `blur(${cfg.blur}) saturate(${cfg.sat}) brightness(${hovering ? 1.04 : 1})`,
            boxShadow: `
              inset 0 1px 0 0 rgba(255, 255, 255, 0.08),
              inset 0 0 0 1px rgba(${glowRgba}, 0.12),
              0 4px 24px -6px rgba(0,0,0,0.5)
            `,
            transform: tilt
              ? `rotateX(${transform.rotateX}deg) rotateY(${transform.rotateY}deg)`
              : undefined,
            transformStyle: tilt ? 'preserve-3d' : undefined,
            transition: 'backdrop-filter 400ms cubic-bezier(0.22,1,0.36,1), transform 200ms ease-out, box-shadow 300ms ease',
          }}
        >
          <div className="pointer-events-none absolute inset-0 rounded-[inherit] bg-gradient-to-b from-white/[0.05] to-transparent" />

          {noise && (
            <div
              className="pointer-events-none absolute inset-0 opacity-[0.015] mix-blend-overlay"
              style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
              }}
            />
          )}

          {sheen && (
            <div
              className="pointer-events-none absolute inset-0 transition-opacity duration-500"
              style={{
                opacity: hovering ? 0.35 : 0,
                background: `radial-gradient(400px circle at ${pos.x}px ${pos.y}px, rgba(${glowRgba}, 0.15), transparent 60%)`,
              }}
            />
          )}

          <div
            className="relative h-full"
            style={{ transform: tilt ? 'translateZ(12px)' : undefined }}
          >
            {children}
          </div>
        </div>
      </div>
    );
  },
);
LiquidGlass.displayName = 'LiquidGlass';

export { LiquidGlass };
