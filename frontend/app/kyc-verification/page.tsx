'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { UserCheck, RefreshCw } from 'lucide-react';
import { KycVerificationTabType } from '@/components/kyc-verification/kyc-verification-types';
import { MOCK_KYC_VERIFICATIONS } from '@/components/kyc-verification/kyc-verification-data';

export default function KycVerificationPage() {
  const [activeTab, setActiveTab] = useState<KycVerificationTabType>('VERIFICATIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_KYC_VERIFICATIONS.filter(k => 
      !search || k.kycId.toLowerCase().includes(search.toLowerCase()) || k.customerRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="kyc-verification">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="KYC & IDENTITY VERIFICATION CONTROL PLANE"
          title="KYC & IDENTITY"
          highlightTitle="VERIFICATION"
          description="Automated document OCR extraction, facial biometric verification, Politically Exposed Persons (PEP) screening, and Tier 1-3 KYC checks."
          icon={UserCheck}
          statusBadge="● KYC ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="VERIFIED PROFILES" value={`${MOCK_KYC_VERIFICATIONS.length}`} subtext="PROCESSED KYC RECORDS" accentColor="text-blue-400" />
          <AGMetricCard label="OCR ACCURACY" value="99.6%" subtext="AUTOMATED EXTRACTION" accentColor="text-emerald-400" />
          <AGMetricCard label="PEP SCREENING" value="100% CLEAR" subtext="ZERO OFAC / PEP MATCHES" accentColor="text-emerald-400" />
          <AGMetricCard label="VERIFICATION SLA" value="< 30s" subtext="REAL-TIME KYC APPROVAL" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search KYC ID, Customer Ref..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['VERIFICATIONS', 'DOCUMENT_OCR', 'FACIAL_BIOMETRICS', 'PEP_CHECKS', 'AUDIT'] as KycVerificationTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'VERIFICATIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">KYC ID</th>
                  <th className="p-3">CUSTOMER REF</th>
                  <th className="p-3">VERIFICATION LEVEL</th>
                  <th className="p-3">OCR SCORE</th>
                  <th className="p-3">PEP SCREENING</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(k => (
                  <tr key={k.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{k.kycId}</td>
                    <td className="p-3 font-bold text-slate-200">{k.customerRef}</td>
                    <td className="p-3 font-bold text-purple-400">{k.verificationLevel}</td>
                    <td className="p-3 font-bold text-emerald-400">{k.ocrScore}</td>
                    <td className="p-3 text-emerald-400 font-bold">{k.pepScreening}</td>
                    <td className="p-3"><AGBadge status={k.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'VERIFICATIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
