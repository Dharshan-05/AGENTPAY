'use client';

import { EnvironmentRecord } from './source-types';
import { Globe, ShieldCheck } from 'lucide-react';

interface SourceEnvironmentsProps {
  environments: EnvironmentRecord[];
}

export function SourceEnvironments({ environments }: SourceEnvironmentsProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Globe className="w-4 h-4 text-blue-600" />
            Environment & Deployment Controls
          </h3>
          <p className="text-xs text-slate-500">Excavated multi-environment configuration panel</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
        {environments.map((env) => (
          <div key={env.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
            <div className="flex justify-between items-center">
              <span className="font-bold text-slate-900 text-sm font-sans">{env.name}</span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                  env.name === 'PRODUCTION'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {env.status}
              </span>
            </div>

            <div className="space-y-1 text-[11px] font-sans">
              <span className="text-slate-500 block font-bold text-[10px] uppercase">CAPABILITIES</span>
              {env.capabilities.map((cap) => (
                <div key={cap} className="flex items-center gap-1.5 text-slate-700 font-semibold">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>{cap}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
