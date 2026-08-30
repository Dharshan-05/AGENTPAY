'use client';

import { SourceApiKeyRecord } from './source-types';
import { Key, Copy, Check, Lock, Eye, Trash2 } from 'lucide-react';
import { useState } from 'react';

interface SourceKeysTableProps {
  keys: SourceApiKeyRecord[];
  onSelectKey: (key: SourceApiKeyRecord) => void;
  onRevokeKey: (id: string) => void;
}

export function SourceKeysTable({ keys, onSelectKey, onRevokeKey }: SourceKeysTableProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const copyKeyPrefix = (id: string, prefix: string) => {
    navigator.clipboard.writeText(prefix);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Key className="w-4 h-4 text-blue-600" />
            API Keys & Secret Bearer Tokens
          </h3>
          <p className="text-xs text-slate-500">Excavated credentials table architecture (Stripe Developer Dashboard source style)</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse font-mono">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Key Name</th>
              <th className="p-3">Token Prefix</th>
              <th className="p-3">Environment</th>
              <th className="p-3">Scope</th>
              <th className="p-3">Created</th>
              <th className="p-3">Last Used</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {keys.map((k) => (
              <tr key={k.id} className="hover:bg-slate-50 transition-colors">
                <td className="p-3 font-bold text-slate-900 font-sans">
                  {k.name}
                  <div className="text-[10px] text-slate-400 font-mono">ID: {k.id}</div>
                </td>

                <td className="p-3">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-slate-700 bg-slate-100 px-2 py-1 rounded border border-slate-200">
                      {k.keyPrefix}••••••••••••
                    </span>
                    <button
                      onClick={() => copyKeyPrefix(k.id, `${k.keyPrefix}••••••••••••`)}
                      className="text-slate-400 hover:text-blue-600 p-1"
                    >
                      {copiedId === k.id ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </td>

                <td className="p-3 font-sans">
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                      k.environment === 'PRODUCTION'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {k.environment}
                  </span>
                </td>

                <td className="p-3 font-sans font-semibold text-slate-700">{k.scope}</td>

                <td className="p-3 text-slate-500 text-[10px]">{k.created}</td>

                <td className="p-3 text-slate-500 text-[10px]">{k.lastUsed}</td>

                <td className="p-3 font-sans">
                  <span
                    className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      k.status === 'ACTIVE'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-slate-200 text-slate-600'
                    }`}
                  >
                    {k.status}
                  </span>
                </td>

                <td className="p-3 text-right font-sans">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => onSelectKey(k)}
                      className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-[11px] font-semibold transition-colors"
                    >
                      Inspect
                    </button>
                    {k.status === 'ACTIVE' && (
                      <button
                        onClick={() => onRevokeKey(k.id)}
                        className="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded-lg text-[11px] font-semibold border border-rose-200 transition-colors"
                      >
                        Revoke
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
