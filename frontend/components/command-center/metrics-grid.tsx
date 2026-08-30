'use client';

import { GlowCard } from '@/components/motion/glow-card';
import { DollarSign, Bot, ShieldCheck, AlertTriangle, TrendingUp, ArrowUpRight } from 'lucide-react';

interface MetricsProps {
  totalVolume: number;
  activeAgents: number;
  totalAgents: number;
  complianceRate: number;
  riskIndex: number;
}

export function MetricsGrid({
  totalVolume,
  activeAgents,
  totalAgents,
  complianceRate,
  riskIndex,
}: MetricsProps) {
  const METRICS = [
    {
      title: '24h Payment Volume',
      value: `$${totalVolume.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      change: '+14.2% vs yesterday',
      icon: DollarSign,
      color: '#10B981',
      badge: 'SETTLED RAIL',
    },
    {
      title: 'Active Agent Fleet',
      value: `${activeAgents} / ${totalAgents}`,
      change: '100% Identity Authenticated',
      icon: Bot,
      color: '#3B82F6',
      badge: 'FLEET ACTIVE',
    },
    {
      title: 'AGENTGUARD Compliance',
      value: `${complianceRate}%`,
      change: '0 Policy Breaches Enforced',
      icon: ShieldCheck,
      color: '#34D399',
      badge: 'POLICY SECURE',
    },
    {
      title: 'FRAUDGUARD Risk Index',
      value: riskIndex.toFixed(2),
      change: riskIndex > 0.3 ? 'Elevated Anomaly Detected' : '0.04 Baseline (Clean)',
      icon: AlertTriangle,
      color: riskIndex > 0.3 ? '#F59E0B' : '#6366F1',
      badge: riskIndex > 0.3 ? 'ATTENTION' : 'LOW RISK',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      {METRICS.map((m) => {
        const Icon = m.icon;
        return (
          <GlowCard
            key={m.title}
            color={m.color}
            className="rounded-2xl bg-slate-900/60 border border-white/[0.08] p-5 hover:border-white/20 transition-colors"
          >
            <div className="flex flex-col justify-between h-full">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase">
                    {m.title}
                  </span>
                  <span
                    className="text-[9px] font-mono px-2 py-0.5 rounded-full border uppercase tracking-wider"
                    style={{
                      backgroundColor: `${m.color}15`,
                      borderColor: `${m.color}30`,
                      color: m.color,
                    }}
                  >
                    {m.badge}
                  </span>
                </div>
                <div className="flex items-baseline justify-between mb-1">
                  <h3 className="text-2xl sm:text-3xl font-mono font-bold text-slate-100 tracking-tight">
                    {m.value}
                  </h3>
                  <Icon className="w-5 h-5 opacity-70" style={{ color: m.color }} />
                </div>
              </div>
              <div className="pt-3 border-t border-white/[0.06] flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3 text-emerald-400" />
                  {m.change}
                </span>
                <ArrowUpRight className="w-3.5 h-3.5 text-slate-600" />
              </div>
            </div>
          </GlowCard>
        );
      })}
    </div>
  );
}
