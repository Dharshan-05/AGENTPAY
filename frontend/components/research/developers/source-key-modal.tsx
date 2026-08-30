'use client';

import { X, Key, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

interface SourceKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateKey: (name: string, env: 'PRODUCTION' | 'SANDBOX', scope: 'FULL_ACCESS' | 'READ_ONLY' | 'PAYMENTS_ONLY') => void;
}

export function SourceKeyModal({ isOpen, onClose, onCreateKey }: SourceKeyModalProps) {
  const [name, setName] = useState('');
  const [env, setEnv] = useState<'PRODUCTION' | 'SANDBOX'>('PRODUCTION');
  const [scope, setScope] = useState<'FULL_ACCESS' | 'READ_ONLY' | 'PAYMENTS_ONLY'>('FULL_ACCESS');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    onCreateKey(name, env, scope);
    setName('');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4 font-sans">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 border border-slate-200">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Key className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-slate-900 text-base">Generate New API Key</h3>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-600 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs font-sans">
          <div>
            <label className="block font-bold text-slate-700 mb-1">Key Name / Description</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Production Agent Deployment Token"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-blue-500 font-medium"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-slate-700 mb-1">Environment</label>
              <select
                value={env}
                onChange={(e) => setEnv(e.target.value as any)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-medium focus:outline-none focus:border-blue-500"
              >
                <option value="PRODUCTION">PRODUCTION</option>
                <option value="SANDBOX">SANDBOX</option>
              </select>
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1">Scope</label>
              <select
                value={scope}
                onChange={(e) => setScope(e.target.value as any)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-medium focus:outline-none focus:border-blue-500"
              >
                <option value="FULL_ACCESS">FULL_ACCESS</option>
                <option value="READ_ONLY">READ_ONLY</option>
                <option value="PAYMENTS_ONLY">PAYMENTS_ONLY</option>
              </select>
            </div>
          </div>

          <div className="pt-2 flex items-center justify-end gap-2 font-semibold">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-sm transition-colors"
            >
              Generate Key
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
