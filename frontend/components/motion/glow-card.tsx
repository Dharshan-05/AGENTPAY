'use client';

import { useRef, useState } from 'react';

interface Props {
  children: React.ReactNode;
  className?: string;
  color?: string;
  size?: number;
}

export function GlowCard({
  children,
  className = '',
  color = '#10B981',
  size = 350,
}: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: -9999, y: -9999 });
  const [hovering, setHovering] = useState(false);

  function handleMove(e: React.MouseEvent<HTMLDivElement>) {
    const rect = ref.current?.getBoundingClientRect();
    if (!rect) return;
    setPos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  }

  return (
    <div
      ref={ref}
      onMouseMove={handleMove}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
      className={`group relative overflow-hidden ${className}`}
      style={
        {
          '--glow-x': `${pos.x}px`,
          '--glow-y': `${pos.y}px`,
          '--glow-size': `${size}px`,
          '--glow-color': color,
        } as React.CSSProperties
      }
    >
      <div
        className="pointer-events-none absolute -inset-px rounded-[inherit] opacity-0 transition-opacity duration-500"
        style={{
          opacity: hovering ? 1 : 0,
          background: `radial-gradient(var(--glow-size) circle at var(--glow-x) var(--glow-y), ${color}, transparent 45%)`,
        }}
      />
      <div className="relative h-full w-full rounded-[inherit] bg-inherit">
        <div
          className="pointer-events-none absolute inset-0 rounded-[inherit] opacity-0 transition-opacity duration-500"
          style={{
            opacity: hovering ? 0.3 : 0,
            background: `radial-gradient(var(--glow-size) circle at var(--glow-x) var(--glow-y), ${color}15, transparent 50%)`,
          }}
        />
        <div className="relative h-full">{children}</div>
      </div>
    </div>
  );
}
