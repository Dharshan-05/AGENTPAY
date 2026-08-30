'use client';

import { TrendingUp, AlertTriangle, Clock, DollarSign, Shield, Zap } from 'lucide-react';

const metrics = [
  {
    label: 'TOTAL VOLUME 24H',
    value: '$1,842,900.00',
    sub: '99.94% Authorization Rate',
    subColor: 'text-emerald-600',
    icon: DollarSign,
    iconBg: 'bg-emerald-50',
    iconColor: 'text-emerald-600',
    border: 'border-emerald-100',
  },
  {
    label: 'ACTIVE PAYMENT INTENTS',
    value: '1,420 ACTIVE',
    sub: 'Avg Latency: 180ms',
    subColor: 'text-blue-600',
    icon: Zap,
    iconBg: 'bg-blue-50',
    iconColor: 'text-blue-600',
    border: 'border-blue-100',
  },
  {
    label: 'UNDER REVIEW / BLOCKED',
    value: '3 BLOCKED',
    sub: '$61,220.00 Risk Hold',
    subColor: 'text-rose-600',
    icon: AlertTriangle,
    iconBg: 'bg-rose-50',
    iconColor: 'text-rose-600',
    border: 'border-rose-100',
  },
  {
    label: 'REFUNDS PROCESSED',
    value: '$2,520.00',
    sub: '0.14% Refund Ratio',
    subColor: 'text-amber-600',
    icon: TrendingUp,
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    border: 'border-amber-100',
  },
  {
    label: 'SETTLEMENT CLEARED',
    value: '$1,781,680.00',
    sub: 'Batch STL-881 Closed',
    subColor: 'text-emerald-600',
    icon: Shield,
    iconBg: 'bg-slate-50',
    iconColor: 'text-slate-600',
    border: 'border-slate-100',
  },
  {
    label: 'REQUIRES HUMAN APPROVAL',
    value: '2 PENDING',
    sub: '$203,420.00 On Hold',
    subColor: 'text-orange-600',
    icon: Clock,
    iconBg: 'bg-orange-50',
    iconColor: 'text-orange-600',
    border: 'border-orange-100',
  },
];

export function SourceMetrics() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 font-sans text-xs">
      {metrics.map((m) => {
        const Icon = m.icon;
        return (
          <div
            key={m.label}
            className={`p-4 bg-white rounded-2xl border ${m.border} shadow-sm space-y-2`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">
                {m.label}
              </span>
              <div className={`p-1.5 ${m.iconBg} rounded-lg`}>
                <Icon className={`w-3.5 h-3.5 ${m.iconColor}`} />
              </div>
            </div>
            <div className="text-lg font-bold text-slate-900 font-mono">{m.value}</div>
            <div className={`text-[10px] font-semibold ${m.subColor}`}>{m.sub}</div>
          </div>
        );
      })}
    </div>
  );
}
