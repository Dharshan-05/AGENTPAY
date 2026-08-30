'use client';

import { SecurityPostureRecord } from './payment-method-types';
import { ShieldCheck, Lock, Key } from 'lucide-react';

interface PaymentMethodSecurityProps {
  records: SecurityPostureRecord[];
}

export function PaymentMethodSecurity({ records }: PaymentMethodSecurityProps) {
  return (
    <div className="space-y-6 font-mono text-xs">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-2">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
            <ShieldCheck className="w-4 h-4" /> PCI SAQ-A OUT OF SCOPE
          </div>
          <p className="text-[11px] text-slate-400 font-sans">
            Zero raw PANs or CVVs stored. All payment methods tokenized via EMVCo network tokens.
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-2">
          <div className="flex items-center gap-2 text-blue-400 font-bold text-xs">
            <Lock className="w-4 h-4" /> HSM ENCLAVE VAULTING
          </div>
          <p className="text-[11px] text-slate-400 font-sans">
            Hardware Security Module AES-256-GCM envelope encryption for ACH bank accounts.
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl space-y-2">
          <div className="flex items-center gap-2 text-purple-400 font-bold text-xs">
            <Key className="w-4 h-4" /> mTLS TRANSPORT ENFORCEMENT
          </div>
          <p className="text-[11px] text-slate-400 font-sans">
            Bidirectional TLS client certificate binding active for sensitive financial payment rails.
          </p>
        </div>
      </div>

      <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">INSTRUMENT</th>
              <th className="px-4 py-3 font-semibold">PCI SCOPE</th>
              <th className="px-4 py-3 font-semibold">VAULT REFERENCE</th>
              <th className="px-4 py-3 font-semibold">FINGERPRINT</th>
              <th className="px-4 py-3 font-semibold">ENCRYPTION</th>
              <th className="px-4 py-3 font-semibold">mTLS STATUS</th>
              <th className="px-4 py-3 font-semibold">LAST ROTATED</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04] text-xs">
            {records.map((sec) => (
              <tr key={sec.id} className="hover:bg-slate-900/40 transition-colors">
                <td className="px-4 py-3.5 font-bold text-slate-200">
                  {sec.instrumentName}
                </td>
                <td className="px-4 py-3.5 font-bold text-emerald-400">
                  {sec.pciScope}
                </td>
                <td className="px-4 py-3.5 font-bold text-blue-400">
                  {sec.vaultReference}
                </td>
                <td className="px-4 py-3.5 text-slate-400 text-[10px]">
                  {sec.tokenFingerprint}
                </td>
                <td className="px-4 py-3.5 text-slate-300">
                  {sec.encryptionAlgorithm}
                </td>
                <td className="px-4 py-3.5 font-bold text-emerald-400">
                  {sec.mTLSStatus}
                </td>
                <td className="px-4 py-3.5 text-slate-400">
                  {sec.secretRotatedAt}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
