'use client';

import React from 'react';

interface AGButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'warning' | 'success' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}

export function AGButton({
  variant = 'primary',
  size = 'md',
  icon: Icon,
  children,
  className = '',
  ...props
}: AGButtonProps) {
  const baseClasses =
    'inline-flex items-center justify-center gap-2 rounded-xl font-mono font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 disabled:opacity-40 disabled:cursor-not-allowed';

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-[11px]',
    md: 'px-4 py-2 text-xs',
    lg: 'px-5 py-2.5 text-sm',
  };

  const variantClasses = {
    primary:
      'bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold shadow-[0_0_20px_rgba(16,185,129,0.25)] border border-emerald-400/60',
    secondary:
      'bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.15)]',
    ghost:
      'bg-slate-900/60 hover:bg-slate-800 text-slate-300 border border-white/[0.08]',
    danger:
      'bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.15)]',
    warning:
      'bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold border border-amber-400 shadow-[0_0_20px_rgba(245,158,11,0.25)]',
    success:
      'bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/40',
    outline:
      'bg-transparent hover:bg-white/[0.04] text-slate-200 border border-white/20',
  };

  return (
    <button
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {Icon && <Icon className="w-3.5 h-3.5 shrink-0" />}
      <span>{children}</span>
    </button>
  );
}
