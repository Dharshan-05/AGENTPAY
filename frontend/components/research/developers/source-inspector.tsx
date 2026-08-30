'use client';

import { SourceApiKeyRecord } from './source-types';
import { X, Key, ShieldCheck, Copy, Check } from 'lucide-react';
import { useState } from 'react';

interface SourceInspectorProps {
  keyItem: SourceApiKeyRecord | null;
  onClose: () => void;
}

export function SourceInspector({ keyItem, onClose }: SourceInspectorProps) {
  const [copied, setCopied] = useState(false);

  if (!keyItem) return null;

  const copyToken = () => {
    navigator.clipboard.writeText(`${keyItem.keyPrefix}••••••••••••`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex justify-end font-sans">
      <div className="w-full max-w-md bg-white h-full shadow-2xl p-6 flex flex-col justify-between overflow-y-auto space-y-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div>
              <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold">API KEY INSPECTOR</span>
              <h2 className="text-lg font-bold text-slate-900">{keyItem.name}</h2>
            </div>
            <button onClick={onClose} className="p-1 rounded hover:bg-slate-100 text-slate-400">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-500">Key ID:</span>
              <span className="font-bold text-slate-900">{keyItem.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Environment:</span>
              <span className="font-bold text-blue-600">{keyItem.environment}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Access Scope:</span>
              <span className="font-bold text-slate-800">{keyItem.scope}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Status:</span>
              <span className="font-bold text-emerald-600">{keyItem.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Created Date:</span>
              <span className="text-slate-600">{keyItem.created}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Last Active:</span>
              <span className="text-slate-600">{keyItem.lastUsed}</span>
            </div>
          </div>

          <div className="p-3.5 bg-slate-900 text-slate-100 rounded-xl font-mono text-xs space-y-1.5">
            <div className="flex justify-between items-center text-[10px] text-slate-400">
              <span>Key Token Pattern:</span>
              <button onClick={copyToken} className="text-blue-400 font-bold flex items-center gap-1">
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                {copied ? 'COPIED' : 'COPY'}
              </button>
            </div>
            <div className="text-emerald-400 font-bold">{keyItem.keyPrefix}••••••••••••</div>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 bg-slate-900 text-white font-bold rounded-xl text-xs hover:bg-slate-800 transition-colors"
        >
          Close Inspector
        </button>
      </div>
    </div>
  );
}
