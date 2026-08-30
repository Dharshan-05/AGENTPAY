'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge, AGBadgeStatus } from '@/components/ui/ag-badge';
import { ProductionAgentSecurityRecord } from './agent-types';
import { Lock } from 'lucide-react';

interface AgentSecurityTableProps {
  securityRecords: ProductionAgentSecurityRecord[];
}

export function AgentSecurityTable({ securityRecords }: AgentSecurityTableProps) {
  const getBadgeStatus = (status: string): AGBadgeStatus => {
    switch (status) {
      case 'VALID':
        return 'APPROVED';
      case 'ROTATION_DUE':
        return 'REVIEW';
      case 'REVOKED':
        return 'BLOCKED';
      default:
        return 'ACTIVE';
    }
  };

  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Lock className="w-4 h-4 text-purple-400" /> mTLS IDENTITY CERTIFICATES & SECURITY POSTURE
          </h3>
          <p className="text-[10px] text-slate-400">Keycloak / Authentik service identity credential rotation and cryptographic audit hashes</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Agent ID</th>
              <th className="p-3.5">Credential Type</th>
              <th className="p-3.5">mTLS Certificate Status</th>
              <th className="p-3.5">Key Fingerprint</th>
              <th className="p-3.5">Last Auth</th>
              <th className="p-3.5">Cryptographic Audit Hash</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {securityRecords.map((s) => (
              <tr key={s.id} className="hover:bg-slate-800/40 cursor-pointer transition-colors">
                <td className="p-3.5 font-bold text-blue-400">{s.agentId}</td>

                <td className="p-3.5 font-bold text-slate-100">{s.credentialType}</td>

                <td className="p-3.5">
                  <AGBadge status={getBadgeStatus(s.mTLSCertificateStatus)} label={`● ${s.mTLSCertificateStatus}`} />
                </td>

                <td className="p-3.5 text-slate-400 text-[10px] font-mono">{s.keyFingerprint}</td>

                <td className="p-3.5 text-slate-300">{s.lastAuthTimestamp}</td>

                <td className="p-3.5 text-emerald-400 text-[10px] font-mono break-all">{s.auditHash}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AGCard>
  );
}
