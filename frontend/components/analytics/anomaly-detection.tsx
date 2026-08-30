'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AnomalyRecord } from './analytics-types';
import { AlertTriangle } from 'lucide-react';

interface AnomalyDetectionProps {
  anomalies: AnomalyRecord[];
}

export function AnomalyDetection({ anomalies }: AnomalyDetectionProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-2 font-bold text-slate-100">
          <AlertTriangle className="w-4 h-4 text-red-400" />
          <span className="text-sm">ANOMALY DETECTION & DEVIATION TELEMETRY</span>
        </div>
        <span className="text-[10px] text-slate-400">Real-Time Behavioral Scan</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Detected Anomaly</th>
              <th className="p-3.5">Severity</th>
              <th className="p-3.5">Agent Persona</th>
              <th className="p-3.5">Risk Score</th>
              <th className="p-3.5">Timestamp</th>
              <th className="p-3.5 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {anomalies.map((a, idx) => (
              <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                <td className="p-3.5 font-bold text-slate-100">{a.anomaly}</td>
                <td className="p-3.5 font-bold text-red-400">{a.severity}</td>
                <td className="p-3.5 text-slate-300">
                  {a.agent} <span className="text-slate-500 text-[10px]">({a.agentId})</span>
                </td>
                <td className="p-3.5 font-bold text-amber-400">{a.riskScore}/100</td>
                <td className="p-3.5 text-slate-400 text-[10px]">{a.detectedAt}</td>
                <td className="p-3.5 text-right">
                  <AGBadge
                    status={
                      a.status === 'INVESTIGATING'
                        ? 'REVIEW'
                        : a.status === 'REVIEW'
                        ? 'PENDING'
                        : 'APPROVED'
                    }
                    label={a.status}
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
