'use client';

import { AG_TOKENS } from '@/lib/design-system';

export type AGBadgeStatus = keyof typeof AG_TOKENS.statusMap | string;

interface AGBadgeProps {
  status: AGBadgeStatus;
  label?: string;
  size?: 'sm' | 'md';
  pulse?: boolean;
}

export function AGBadge({ status, label, size = 'sm', pulse = true }: AGBadgeProps) {
  const normKey = status.toUpperCase().replace(/\s+/g, '_') as keyof typeof AG_TOKENS.statusMap;
  const config = AG_TOKENS.statusMap[normKey] || {
    label: status,
    bg: 'bg-slate-800',
    text: 'text-slate-300',
    border: 'border-white/10',
    dot: 'bg-slate-400',
  };

  const displayText = label || config.label;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-mono font-bold tracking-wider border backdrop-blur-md transition-all ${
        size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-3 py-1 text-xs'
      } ${config.bg} ${config.text} ${config.border}`}
    >
      {pulse && <span className={`w-1.5 h-1.5 rounded-full ${config.dot} animate-pulse`} />}
      <span>{displayText}</span>
    </span>
  );
}
