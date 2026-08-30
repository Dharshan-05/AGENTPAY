'use client';

import React from 'react';

interface BaseCardProps {
  children: React.ReactNode;
  className?: string;
}

export function AGCard({ children, className = '' }: BaseCardProps) {
  return (
    <div
      className={`p-5 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl transition-all ${className}`}
    >
      {children}
    </div>
  );
}

export function AGGlassCard({ children, className = '' }: BaseCardProps) {
  return (
    <div
      className={`p-6 rounded-2xl bg-slate-900/80 border border-white/[0.1] backdrop-blur-2xl shadow-2xl ${className}`}
    >
      {children}
    </div>
  );
}

export function AGInteractiveCard({
  children,
  onClick,
  className = '',
}: BaseCardProps & { onClick?: () => void }) {
  return (
    <div
      onClick={onClick}
      className={`p-5 rounded-2xl bg-slate-900/60 border border-white/[0.08] hover:border-emerald-500/40 hover:bg-slate-900/90 transition-all cursor-pointer group ${className}`}
    >
      {children}
    </div>
  );
}

interface AGMetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  trend?: string;
  trendPositive?: boolean;
  accentColor?: string;
}

export function AGMetricCard({
  label,
  value,
  subtext,
  trend,
  trendPositive = true,
  accentColor = 'text-slate-100',
}: AGMetricCardProps) {
  return (
    <AGCard className="relative overflow-hidden group">
      <div className="flex items-center justify-between text-slate-400 font-mono text-[10px] uppercase tracking-wider mb-2">
        <span>{label}</span>
        {trend && (
          <span
            className={`font-bold ${
              trendPositive ? 'text-emerald-400' : 'text-red-400'
            }`}
          >
            {trend}
          </span>
        )}
      </div>
      <p className={`font-display text-3xl font-bold tracking-tight ${accentColor}`}>
        {value}
      </p>
      {subtext && (
        <p className="text-xs font-mono text-slate-500 mt-2 uppercase tracking-wide">
          {subtext}
        </p>
      )}
    </AGCard>
  );
}

export function AGStatusCard({
  title,
  status,
  description,
  children,
}: {
  title: string;
  status: React.ReactNode;
  description?: string;
  children?: React.ReactNode;
}) {
  return (
    <AGGlassCard className="space-y-4">
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
        <div>
          <h3 className="font-display font-bold text-base text-slate-100">{title}</h3>
          {description && (
            <p className="text-xs font-mono text-slate-400 mt-0.5">{description}</p>
          )}
        </div>
        <div>{status}</div>
      </div>
      {children}
    </AGGlassCard>
  );
}
