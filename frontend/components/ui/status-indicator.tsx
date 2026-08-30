'use client';

import React from 'react';

interface StatusIndicatorProps {
  status?: 'online' | 'warning' | 'error' | 'offline';
  pulse?: boolean;
  label?: string;
  className?: string;
}

export function StatusIndicator({
  status = 'online',
  pulse = true,
  label,
  className = '',
}: StatusIndicatorProps) {
  const colors = {
    online: 'bg-emerald-400',
    warning: 'bg-amber-400',
    error: 'bg-red-400',
    offline: 'bg-slate-500',
  };

  return (
    <div className={`inline-flex items-center gap-2 font-mono text-xs ${className}`}>
      <span className="relative flex h-2.5 w-2.5">
        {pulse && (
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full ${colors[status]} opacity-75`}
          />
        )}
        <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${colors[status]}`} />
      </span>
      {label && <span className="text-slate-300 font-medium">{label}</span>}
    </div>
  );
}
