'use client';

import { WebhookSecurityRecord } from './source-types';

interface SourceSecurityProps {
  records: WebhookSecurityRecord[];
}

export function SourceSecurity({ records }: SourceSecurityProps) {
  return (
    <div className="space-y-6 font-sans">
      <div className="bg-purple-50 p-4 rounded-2xl border border-purple-200 flex items-center justify-between gap-3 text-xs">
        <div>
          <h3 className="font-bold text-purple-900">WEBHOOK SIGNATURE &amp; mTLS SECURITY POSTURE</h3>
          <p className="text-purple-700 mt-0.5">
            All outgoing webhooks are signed using HMAC-SHA256 with timestamp tolerance validation and strict mTLS verification.
          </p>
        </div>
        <span className="px-3 py-1 bg-purple-600 text-white font-mono font-bold rounded-lg text-[11px]">
          HMAC-SHA256 ENFORCED
        </span>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-mono text-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-[10px] text-slate-500 uppercase tracking-wider">
                <th className="px-4 py-3 font-semibold">ENDPOINT ID</th>
                <th className="px-4 py-3 font-semibold">ENDPOINT NAME</th>
                <th className="px-4 py-3 font-semibold">SIGNING SECRET</th>
                <th className="px-4 py-3 font-semibold">ALGORITHM</th>
                <th className="px-4 py-3 font-semibold">mTLS STATUS</th>
                <th className="px-4 py-3 font-semibold">TOLERANCE</th>
                <th className="px-4 py-3 font-semibold">IP ALLOWLIST</th>
                <th className="px-4 py-3 font-semibold">ROTATION DUE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {records.map((sec) => (
                <tr key={sec.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3.5 font-bold text-purple-700">
                    {sec.endpointId}
                  </td>
                  <td className="px-4 py-3.5 text-slate-900 font-sans font-bold">
                    {sec.endpointName}
                  </td>
                  <td className="px-4 py-3.5 text-slate-600 font-mono">
                    {sec.secretMasked}
                  </td>
                  <td className="px-4 py-3.5 font-bold text-slate-700">
                    {sec.signatureAlgorithm}
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      sec.mTLSStatus === 'ENFORCED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-100 text-slate-600 border-slate-200'
                    }`}>
                      {sec.mTLSStatus}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-slate-600">
                    {sec.timestampToleranceSeconds}s
                  </td>
                  <td className="px-4 py-3.5 text-slate-500 text-[11px]">
                    {sec.ipAllowlist.join(', ')}
                  </td>
                  <td className="px-4 py-3.5 font-bold text-amber-600">
                    {sec.secretRotationDueDays} Days
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
