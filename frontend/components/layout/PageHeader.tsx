'use client';

import React from 'react';

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  highlightTitle?: string;
  description: string;
  icon?: React.ComponentType<{ className?: string }>;
  statusBadge?: React.ReactNode;
  actions?: React.ReactNode;
}

export function PageHeader({
  eyebrow = 'OPERATIONAL MODULE',
  title,
  highlightTitle,
  description,
  icon: Icon,
  statusBadge,
  actions,
}: PageHeaderProps) {
  return (
    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b border-white/[0.08]">
      <div className="flex items-start gap-3.5">
        {Icon && (
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold shrink-0 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
            <Icon className="w-5 h-5" />
          </div>
        )}

        <div>
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-mono tracking-[0.2em] text-emerald-400 uppercase font-bold">
              {eyebrow}
            </span>
            {statusBadge}
          </div>

          <h1 className="font-display text-2xl font-bold text-slate-100 tracking-wider mt-0.5">
            {title}{' '}
            {highlightTitle && (
              <span className="text-emerald-400">{highlightTitle}</span>
            )}
          </h1>

          <p className="text-xs font-mono text-slate-400 mt-1 max-w-3xl leading-relaxed">
            {description}
          </p>
        </div>
      </div>

      {actions && <div className="flex flex-wrap items-center gap-3">{actions}</div>}
    </div>
  );
}
