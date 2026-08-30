'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { MerchantCategoryRecord } from './analytics-types';
import { ShoppingBag } from 'lucide-react';

interface MerchantAnalyticsProps {
  merchants: MerchantCategoryRecord[];
}

export function MerchantAnalytics({ merchants }: MerchantAnalyticsProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-2 font-bold text-slate-100">
          <ShoppingBag className="w-4 h-4 text-emerald-400" />
          <span className="text-sm">MERCHANT & CATEGORY INTELLIGENCE</span>
        </div>
        <span className="text-[10px] text-slate-400">Target Categories</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Merchant Target</th>
              <th className="p-3.5">Category</th>
              <th className="p-3.5">Volume</th>
              <th className="p-3.5">Risk Score</th>
              <th className="p-3.5">Success Rate</th>
              <th className="p-3.5 text-right">Decision</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {merchants.map((m) => (
              <tr key={m.merchant} className="hover:bg-slate-800/40 transition-colors">
                <td className="p-3.5 font-bold text-slate-100">{m.merchant}</td>
                <td className="p-3.5 text-slate-300">{m.category}</td>
                <td className="p-3.5 font-bold text-emerald-400">{m.volume}</td>
                <td className="p-3.5 font-bold text-amber-400">{m.riskScore}</td>
                <td className="p-3.5 text-emerald-400 font-bold">{m.successRate}</td>
                <td className="p-3.5 text-right">
                  <AGBadge
                    status={
                      m.decision === 'AUTHORIZED'
                        ? 'APPROVED'
                        : m.decision === 'BLOCKED'
                        ? 'BLOCKED'
                        : 'REVIEW'
                    }
                    label={m.decision}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AGCard>
  );
}
