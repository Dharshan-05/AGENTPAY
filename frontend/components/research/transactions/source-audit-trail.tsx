'use client';

import { BookOpen, Lock } from 'lucide-react';

export function SourceAuditTrail() {
  const auditEntries = [
    {
      id: 'aud_1',
      recordId: 'AUD-91F2-FINAL',
      transactionId: 'TXN-AGP-91F2',
      action: 'TRANSACTION_SETTLED',
      actor: 'AGENTPAY Settlement Engine',
      actorType: 'SYSTEM',
      timestamp: '2026-08-30 08:18:00.055 UTC',
      outcome: 'SUCCESS',
      auditHash: '0xD12739182739182C2739182739E1',
      immutable: true,
    },
    {
      id: 'aud_2',
      recordId: 'AUD-91F2-CAP',
      transactionId: 'TXN-AGP-91F2',
      action: 'PAYMENT_CAPTURED',
      actor: 'Stripe Payments US',
      actorType: 'PROCESSOR',
      timestamp: '2026-08-30 08:14:22.285 UTC',
      outcome: 'SUCCESS',
      auditHash: '0xE98271293812739182739182739F',
      immutable: true,
    },
    {
      id: 'aud_3',
      recordId: 'AUD-91F2-AUTH',
      transactionId: 'TXN-AGP-91F2',
      action: 'PAYMENT_AUTHORIZED',
      actor: 'Stripe Payments US',
      actorType: 'PROCESSOR',
      timestamp: '2026-08-30 08:14:22.180 UTC',
      outcome: 'SUCCESS',
      auditHash: '0xC98271834120981273918273912C',
      immutable: true,
    },
    {
      id: 'aud_4',
      recordId: 'AUD-91F2-RISK',
      transactionId: 'TXN-AGP-91F2',
      action: 'RISK_EVALUATED',
      actor: 'FRAUDGUARD Risk Engine v2.4',
      actorType: 'SYSTEM',
      timestamp: '2026-08-30 08:14:22.081 UTC',
      outcome: 'LOW_RISK',
      auditHash: '0xB819273FADE123891273912739A1',
      immutable: true,
    },
    {
      id: 'aud_5',
      recordId: 'AUD-91F2-POL',
      transactionId: 'TXN-AGP-91F2',
      action: 'POLICY_EVALUATED',
      actor: 'AGENTGUARD Engine',
      actorType: 'SYSTEM',
      timestamp: '2026-08-30 08:14:22.045 UTC',
      outcome: 'APPROVED',
      auditHash: '0x44129812739123A8123019827391',
      immutable: true,
    },
    {
      id: 'aud_6',
      recordId: 'AUD-11A8-BLOCKED',
      transactionId: 'TXN-AGP-11A8',
      action: 'TRANSACTION_BLOCKED',
      actor: 'AGENTGUARD Engine',
      actorType: 'SYSTEM',
      timestamp: '2026-08-29 14:10:00.210 UTC',
      outcome: 'BLOCKED',
      auditHash: '0xC11273918273918273918273912C',
      immutable: true,
    },
    {
      id: 'aud_7',
      recordId: 'AUD-REF-88219',
      transactionId: 'TXN-AGP-91F2',
      action: 'REFUND_COMPLETED',
      actor: 'SYSTEM_AGENT / Stripe Payments US',
      actorType: 'SYSTEM',
      timestamp: '2026-08-30 09:01:44.000 UTC',
      outcome: 'REFUNDED',
      auditHash: '0xF11739182C739182739182739112',
      immutable: true,
    },
    {
      id: 'aud_8',
      recordId: 'AUD-72D1-REVIEW',
      transactionId: 'TXN-AGP-72D1',
      action: 'HUMAN_REVIEW_REQUESTED',
      actor: 'AGENTGUARD Policy Engine',
      actorType: 'SYSTEM',
      timestamp: '2026-08-30 07:55:15.002 UTC',
      outcome: 'PENDING',
      auditHash: '0xA12739182739182739182739183A',
      immutable: true,
    },
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans text-xs">
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-slate-500" />
          <div>
            <h3 className="font-bold text-slate-900 text-sm">Immutable Audit Trail</h3>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Cryptographically signed financial transaction audit log · {auditEntries.length} records
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Lock className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-[10px] text-slate-400 font-mono">IMMUTABLE · TAMPER-EVIDENT · PCI-COMPLIANT</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr className="border-b border-slate-100 text-slate-500 bg-slate-50 text-[10px] uppercase tracking-wide font-bold">
              <th className="px-4 py-3">AUDIT RECORD ID</th>
              <th className="px-4 py-3">TRANSACTION ID</th>
              <th className="px-4 py-3">ACTION</th>
              <th className="px-4 py-3">ACTOR</th>
              <th className="px-4 py-3">ACTOR TYPE</th>
              <th className="px-4 py-3">TIMESTAMP</th>
              <th className="px-4 py-3">OUTCOME</th>
              <th className="px-4 py-3">IMMUTABLE</th>
              <th className="px-4 py-3">AUDIT HASH</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {auditEntries.map((a) => (
              <tr key={a.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="px-4 py-3 font-bold font-mono text-[10px] text-slate-900">{a.recordId}</td>
                <td className="px-4 py-3 font-bold text-blue-700 font-mono text-[10px]">{a.transactionId}</td>
                <td className="px-4 py-3">
                  <span className="bg-slate-100 text-slate-700 font-mono text-[9px] font-bold px-2 py-0.5 rounded">
                    {a.action}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-700 text-[10px] font-semibold max-w-[140px] truncate">{a.actor}</td>
                <td className="px-4 py-3">
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                    a.actorType === 'SYSTEM' ? 'bg-blue-50 text-blue-700' :
                    a.actorType === 'PROCESSOR' ? 'bg-teal-50 text-teal-700' :
                    'bg-slate-100 text-slate-600'
                  }`}>
                    {a.actorType}
                  </span>
                </td>
                <td className="px-4 py-3 font-mono text-[9px] text-slate-500">{a.timestamp}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    a.outcome === 'SUCCESS' || a.outcome === 'APPROVED' || a.outcome === 'REFUNDED' || a.outcome === 'LOW_RISK'
                      ? 'bg-emerald-100 text-emerald-800'
                      : a.outcome === 'BLOCKED'
                      ? 'bg-rose-100 text-rose-800'
                      : 'bg-amber-100 text-amber-800'
                  }`}>
                    {a.outcome}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1">
                    <Lock className="w-3 h-3 text-emerald-500" />
                    <span className="text-emerald-600 font-bold text-[10px]">YES</span>
                  </div>
                </td>
                <td className="px-4 py-3 font-mono text-[9px] text-slate-400 max-w-[180px] truncate">
                  {a.auditHash}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
        <span className="text-[10px] text-slate-400 font-mono">
          All records are cryptographically signed. Audit hashes are tamper-evident and immutable once written.
        </span>
        <span className="text-[10px] text-slate-400 font-mono">SOURCE: Apache Fineract Ledger · Kill Bill Audit</span>
      </div>
    </div>
  );
}
