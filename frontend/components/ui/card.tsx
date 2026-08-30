'use client';

import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: 'default' | 'glow' | 'subtle';
  className?: string;
}

export function Card({ children, variant = 'default', className = '', ...props }: CardProps) {
  const baseStyle =
    'rounded-2xl backdrop-blur-xl transition-all duration-300 relative overflow-hidden';

  const variantStyles = {
    default: 'bg-slate-950/80 border border-white/[0.08] hover:border-white/[0.15]',
    glow: 'bg-slate-950/90 border border-emerald-500/20 hover:border-emerald-500/40 shadow-[0_0_20px_rgba(16,185,129,0.1)] hover:shadow-[0_0_30px_rgba(16,185,129,0.2)]',
    subtle: 'bg-slate-900/40 border border-white/[0.04] hover:bg-slate-900/60',
  };

  return (
    <div className={`${baseStyle} ${variantStyles[variant]} ${className}`} {...props}>
      {children}
    </div>
  );
}
