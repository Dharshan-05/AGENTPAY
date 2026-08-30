'use client';

import React from 'react';

type BadgeVariant =
  | 'AUTHORIZED'
  | 'REVIEW'
  | 'BLOCKED'
  | 'ACTIVE'
  | 'PENDING_APPROVAL'
  | 'HIGH_RISK'
  | 'SUSPENDED'
  | 'POLICY'
  | 'INFO';

interface BadgeProps {
  variant: BadgeVariant;
  children?: React.ReactNode;
  className?: string;
}

export function Badge({ variant, children, className = '' }: BadgeProps) {
  const styles: Record<BadgeVariant, string> = {
    AUTHORIZED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    ACTIVE: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    REVIEW: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    PENDING_APPROVAL: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    BLOCKED: 'bg-red-500/10 text-red-400 border-red-500/30',
    HIGH_RISK: 'bg-red-500/10 text-red-400 border-red-500/30',
    SUSPENDED: 'bg-red-500/20 text-red-400 border-red-500/40',
    POLICY: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    INFO: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-[10px] font-mono font-bold uppercase tracking-wider ${styles[variant]} ${className}`}
    >
      {children || variant.replace('_', ' ')}
    </span>
  );
}
