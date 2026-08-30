'use client';

import { WebhookSecurityRecord } from './webhook-types';
import { AGBadge } from '@/components/ui/ag-badge';
import { ShieldCheck, Key, Lock, RefreshCw } from 'lucide-react';

interface WebhookSecurityProps {
  records: WebhookSecurityRecord[];
}

export function WebhookSecurity({ records }: WebhookSecurityProps) {
  return (
    <div className="space-y-6 font-mono text-xs">
      {/* SECURITY OVERVIEW CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-2">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
            <ShieldCheck className="w-4 h-4" /> ZERO-TRUST SIGNATURE VERIFICATION
          </div>
          <p className="text-[11px] text-slate-400 font-sans">
            Every payload signed with HMAC-SHA256 timestamped signatures against replay attacks.
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-2">
          <div className="flex items-center gap-2 text-blue-400 font-bold text-xs">
            <Lock className="w-4 h-4" /> mTLS TRANSPORT ENFORCEMENT
          </div>
          <p className="text-[11px] text-slate-400 font-sans">
            Bidirectional TLS client certificate binding active for sensitive financial webhooks.
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-2">
          <div className="flex items-center gap-2 text-purple-400 font-bold text-xs">
            <RefreshCw className="w-4 h-4" /> AUTOMATED SECRET ROTATION
          </div>
          <p className="text-[11px] text-slate-400 font-sans">
            Dual-signing secret rotation active with 24-hour overlap windows.
          </p>
        </div>
      </div>

      {/* SECURITY TABLE */}
      <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">ENDPOINT</th>
              <th className="px-4 py-3 font-semibold">SIGNING SECRET</th>
              <th className="px-4 py-3 font-semibold">ALGORITHM</th>
              <th className="px-4 py-3 font-semibold">mTLS STATUS</th>
              <th className="px-4 py-3 font-semibold">TOLERANCE</th>
              <th className="px-4 py-3 font-semibold">LAST ROTATED</th>
              <th className="px-4 py-3 font-semibold">ROTATION DUE</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04] text-xs">
            {records.map((sec) => (
              <tr key={sec.id} className="hover:bg-slate-900/40 transition-colors">
                <td className="px-4 py-3.5 font-bold text-slate-200">
                  {sec.endpointName}
                </td>
                <td className="px-4 py-3.5 font-bold text-blue-400">
                  {sec.secretMasked}
                </td>
                <td className="px-4 py-3.5 text-slate-300">
                  {sec.signatureAlgorithm}
                </td>
                <td className="px-4 py-3.5">
                  <AGBadge status={sec.mTLSStatus} size="sm" />
                </td>
                <td className="px-4 py-3.5 text-slate-400">
                  {sec.timestampToleranceSeconds}s
                </td>
                <td className="px-4 py-3.5 text-slate-400">
                  {sec.secretRotatedAt}
                </td>
                <td className="px-4 py-3.5 font-bold text-amber-400">
                  IN {sec.secretRotationDueDays} DAYS
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
