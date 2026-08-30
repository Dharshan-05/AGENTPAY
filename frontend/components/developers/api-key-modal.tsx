'use client';

import { AGModal } from '@/components/ui/ag-modal';
import { AGButton } from '@/components/ui/ag-button';
import { Key, Copy, Check, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

interface ApiKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateKey: (name: string, env: 'PRODUCTION' | 'SANDBOX', scopeStr: string) => void;
}

export function ApiKeyModal({ isOpen, onClose, onCreateKey }: ApiKeyModalProps) {
  const [name, setName] = useState('');
  const [env, setEnv] = useState<'PRODUCTION' | 'SANDBOX'>('PRODUCTION');
  const [scopes, setScopes] = useState<string[]>(['payments:write', 'agents:read']);
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [copiedToken, setCopiedToken] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    const keyVal = `sk_${env.toLowerCase()}_agp_${Math.random().toString(36).substring(2, 10)}`;
    setGeneratedKey(keyVal);
    onCreateKey(name, env, scopes.join(', '));
  };

  const copyToken = () => {
    if (!generatedKey) return;
    navigator.clipboard.writeText(generatedKey);
    setCopiedToken(true);
    setTimeout(() => setCopiedToken(false), 2000);
  };

  const toggleScope = (scope: string) => {
    setScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]
    );
  };

  return (
    <AGModal
      isOpen={isOpen}
      onClose={() => {
        setGeneratedKey(null);
        onClose();
      }}
      title={generatedKey ? "CREDENTIAL GENERATED DEMO TOKEN" : "CREATE PRODUCTION API KEY"}
      subtitle={generatedKey ? "SECURITY DEMO BEARER TOKEN GENERATED" : "ZERO-TRUST GOVERNED CREDENTIAL CREATION"}
    >
      {generatedKey ? (
        <div className="space-y-4 font-mono text-xs">
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-2">
            <div className="flex justify-between items-center text-emerald-400 font-bold">
              <span className="flex items-center gap-1.5"><ShieldCheck className="w-4 h-4" /> DEMO TOKEN CREATED</span>
              <span>LIVE</span>
            </div>
            <p className="text-[10px] text-slate-400">
              This simulated bearer token will only be shown once. Please store it securely in your agent environment variables.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950 border border-white/10 flex items-center justify-between font-mono text-xs">
            <span className="text-emerald-400 font-bold">{generatedKey}</span>
            <button onClick={copyToken} className="text-blue-400 font-bold flex items-center gap-1">
              {copiedToken ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copiedToken ? 'COPIED' : 'COPY'}
            </button>
          </div>

          <div className="pt-2 flex justify-end">
            <AGButton variant="primary" size="md" onClick={() => {
              setGeneratedKey(null);
              onClose();
            }}>
              DONE & DISMISS
            </AGButton>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4 font-mono text-xs">
          <div>
            <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
              Key Name / Description
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Procurement Agent Production Token"
              className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500/50"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
                Environment
              </label>
              <select
                value={env}
                onChange={(e) => setEnv(e.target.value as any)}
                className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500/50"
              >
                <option value="PRODUCTION">PRODUCTION</option>
                <option value="SANDBOX">SANDBOX</option>
              </select>
            </div>

            <div>
              <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
                Rotation Policy
              </label>
              <select className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500/50">
                <option value="30">30 DAYS (ENFORCED)</option>
                <option value="90">90 DAYS</option>
                <option value="180">180 DAYS</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-2 font-bold">
              Granted Scopes
            </label>
            <div className="grid grid-cols-2 gap-2 text-[10px]">
              {[
                'payments:read',
                'payments:write',
                'agents:read',
                'agentguard:evaluate',
                'fraudguard:read',
                'webhooks:write',
              ].map((sc) => {
                const isChecked = scopes.includes(sc);
                return (
                  <button
                    key={sc}
                    type="button"
                    onClick={() => toggleScope(sc)}
                    className={`p-2 rounded-lg border text-left flex items-center justify-between ${
                      isChecked
                        ? 'bg-blue-500/10 border-blue-500/40 text-blue-400 font-bold'
                        : 'bg-slate-950/60 border-white/[0.06] text-slate-400'
                    }`}
                  >
                    <span>{sc}</span>
                    {isChecked && <Check className="w-3 h-3 text-blue-400" />}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="pt-2 flex items-center justify-end gap-2">
            <AGButton variant="ghost" size="md" onClick={onClose} type="button">
              CANCEL
            </AGButton>
            <AGButton variant="primary" size="md" type="submit">
              CREATE KEY
            </AGButton>
          </div>
        </form>
      )}
    </AGModal>
  );
}
