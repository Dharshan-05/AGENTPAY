'use client';

import { DeveloperApiKey } from './developers-types';
import { ApiKeyStatusBadge } from './api-key-status';
import { AGButton } from '@/components/ui/ag-button';
import { Key, Copy, Check } from 'lucide-react';
import { useState } from 'react';

interface ApiKeysTableProps {
  keys: DeveloperApiKey[];
  selectedKeyId: string | null;
  onSelectKey: (id: string) => void;
  onRevokeKey: (id: string) => void;
}

export function ApiKeysTable({ keys, selectedKeyId, onSelectKey, onRevokeKey }: ApiKeysTableProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const copyPrefix = (id: string, prefix: string) => {
    navigator.clipboard.writeText(prefix);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="rounded-2xl border border-white/[0.08] bg-slate-900/60 overflow-hidden backdrop-blur-xl font-mono text-xs shadow-2xl space-y-4 p-4">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Key className="w-4 h-4 text-emerald-400" /> PRODUCTION & SANDBOX CREDENTIALS
          </h3>
          <p className="text-[10px] text-slate-400">Bearer tokens for autonomous agents and trusted integrations</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Status</th>
              <th className="p-3.5">Key Name & ID</th>
              <th className="p-3.5">Token Prefix</th>
              <th className="p-3.5">Environment</th>
              <th className="p-3.5">Scopes</th>
              <th className="p-3.5">Created</th>
              <th className="p-3.5">Last Used</th>
              <th className="p-3.5">Req Rate</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {keys.map((k) => {
              const isSelected = selectedKeyId === k.id;
              return (
                <tr
                  key={k.id}
                  onClick={() => onSelectKey(k.id)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-blue-500/10 border-l-2 border-l-blue-400'
                      : 'hover:bg-slate-800/40'
                  }`}
                >
                  <td className="p-3.5">
                    <ApiKeyStatusBadge status={k.status} />
                  </td>

                  <td className="p-3.5 font-bold text-slate-100">
                    <div>{k.name}</div>
                    <div className="text-[10px] text-slate-500 font-normal">{k.id}</div>
                  </td>

                  <td className="p-3.5">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-emerald-400 bg-slate-950 px-2.5 py-1 rounded border border-white/10 text-[11px] font-bold">
                        {k.keyPrefix}
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          copyPrefix(k.id, k.keyPrefix);
                        }}
                        className="text-slate-400 hover:text-blue-400"
                      >
                        {copiedId === k.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </td>

                  <td className="p-3.5">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border ${
                        k.environment === 'PRODUCTION'
                          ? 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      }`}
                    >
                      {k.environment}
                    </span>
                  </td>

                  <td className="p-3.5">
                    <div className="flex flex-wrap gap-1">
                      {k.scopes.map((s) => (
                        <span key={s} className="px-1.5 py-0.5 rounded bg-slate-950 text-slate-300 text-[9px] border border-white/[0.06]">
                          {s}
                        </span>
                      ))}
                    </div>
                  </td>

                  <td className="p-3.5 text-slate-400 text-[10px]">{k.created}</td>

                  <td className="p-3.5 text-slate-400 text-[10px]">{k.lastUsed}</td>

                  <td className="p-3.5 font-bold text-blue-400">{k.requestRate}</td>

                  <td className="p-3.5 text-right">
                    <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                      <AGButton variant="ghost" size="sm" onClick={() => onSelectKey(k.id)}>
                        Inspect
                      </AGButton>
                      {k.status === 'ACTIVE' && (
                        <AGButton variant="danger" size="sm" onClick={() => onRevokeKey(k.id)}>
                          Revoke
                        </AGButton>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
