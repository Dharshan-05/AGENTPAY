'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { SettlementRecord } from './types';
import { Building2, ArrowUpRight } from 'lucide-react';

interface SettlementsProps {
  settlements: SettlementRecord[];
}

export function Settlements({ settlements }: SettlementsProps) {
  return (
    <div className="space-y-6 font-mono text-xs">
      {/* SETTLEMENT KPI METRICS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">AVAILABLE BALANCE</span>
          <div className="text-xl font-bold text-emerald-400">$138,564.50</div>
          <span className="text-[10px] text-slate-500">Ready for instant payout</span>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">PENDING SETTLEMENT</span>
          <div className="text-xl font-bold text-amber-400">$24,820.00</div>
          <span className="text-[10px] text-slate-500">Clearing in 12 hours</span>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">TODAY'S PAYOUT</span>
          <div className="text-xl font-bold text-slate-100">$40,914.60</div>
          <span className="text-[10px] text-slate-500">Batch #po_8812A · Cleared</span>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">NEXT SCHEDULE</span>
          <div className="text-xl font-bold text-blue-400">T+1 AUTOMATED</div>
          <span className="text-[10px] text-slate-500">Daily wire at 23:00 UTC</span>
        </div>
      </div>

      {/* SETTLEMENT BATCH TABLE */}
      <AGCard className="space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
          <span className="font-bold text-slate-100 flex items-center gap-2 text-sm">
            <Building2 className="w-4 h-4 text-blue-400" /> SETTLEMENT BATCH HISTORY
          </span>
          <AGBadge status="POLICY_SECURE" label="INSTANT CLEARING" />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
                <th className="p-3.5">Settlement ID</th>
                <th className="p-3.5">Gross Volume</th>
                <th className="p-3.5">Fees</th>
                <th className="p-3.5">Net Payout</th>
                <th className="p-3.5">Destination Bank</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Payout Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04]">
              {settlements.map((s) => (
                <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3.5 font-bold text-slate-100">{s.id}</td>
                  <td className="p-3.5 font-bold text-slate-200">{s.grossAmount}</td>
                  <td className="p-3.5 text-slate-400">{s.feeAmount}</td>
                  <td className="p-3.5 font-bold text-emerald-400">{s.netAmount}</td>
                  <td className="p-3.5 text-slate-300">{s.bankDestination}</td>
                  <td className="p-3.5">
                    <AGBadge status={s.status === 'SETTLED' ? 'APPROVED' : 'PENDING'} label={`● ${s.status}`} />
                  </td>
                  <td className="p-3.5 text-slate-400 text-[10px]">{s.payoutDate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </AGCard>
    </div>
  );
}
