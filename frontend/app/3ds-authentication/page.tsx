'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { ShieldCheck, RefreshCw } from 'lucide-react';
import { ThreeDSAuthenticationTabType } from '@/components/3ds-authentication/3ds-authentication-types';
import { MOCK_3DS_AUTHENTICATIONS } from '@/components/3ds-authentication/3ds-authentication-data';

export default function ThreeDSAuthenticationPage() {
  const [activeTab, setActiveTab] = useState<ThreeDSAuthenticationTabType>('AUTHENTICATIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_3DS_AUTHENTICATIONS.filter(t => 
      !search || t.threeDSId.toLowerCase().includes(search.toLowerCase()) || t.paymentIntentRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="3ds-authentication">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="3D SECURE 2.0 AUTHENTICATION & PSD2 SCA ENGINE PLANE"
          title="3D SECURE 2.0"
          highlightTitle="AUTHENTICATION"
          description="EMV 3DS 2.0 protocol engine, frictionless flow optimization, TRA exemption routing, and liability shift verification."
          icon={ShieldCheck}
          statusBadge="● 3DS 2.0 PROTOCOL ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="3DS AUTHENTICATIONS" value={`${MOCK_3DS_AUTHENTICATIONS.length}`} subtext="PROCESSED SCA FLOWS" accentColor="text-blue-400" />
          <AGMetricCard label="FRICTIONLESS RATE" value="92.4%" subtext="ZERO USER FRICTION" accentColor="text-emerald-400" />
          <AGMetricCard label="LIABILITY SHIFT" value="100% SHIFTED" subtext="ISSUER FRAUD LIABILITY" accentColor="text-emerald-400" />
          <AGMetricCard label="PSD2 COMPLIANCE" value="SCA VERIFIED" subtext="EU COMPLIANCE MET" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search 3DS ID, Payment Intent Ref..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['AUTHENTICATIONS', 'FRICTIONLESS', 'CHALLENGES', 'EXEMPTION_ENGINE', 'AUDIT'] as ThreeDSAuthenticationTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'AUTHENTICATIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">3DS ID</th>
                  <th className="p-3">PAYMENT INTENT REF</th>
                  <th className="p-3">AUTH FLOW</th>
                  <th className="p-3">CAVV RESULT</th>
                  <th className="p-3">DS TRANSACTION ID</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(t => (
                  <tr key={t.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{t.threeDSId}</td>
                    <td className="p-3 font-bold text-purple-400">{t.paymentIntentRef}</td>
                    <td className="p-3 font-bold text-emerald-400">{t.authFlow}</td>
                    <td className="p-3 text-slate-300 font-mono">{t.cavvResult}</td>
                    <td className="p-3 text-slate-400 font-mono">{t.dsTransactionId}</td>
                    <td className="p-3"><AGBadge status={t.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'AUTHENTICATIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
