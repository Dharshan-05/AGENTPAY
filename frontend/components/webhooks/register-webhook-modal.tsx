'use client';

import { useState } from 'react';
import { AGButton } from '@/components/ui/ag-button';
import { X, Radio, ShieldCheck } from 'lucide-react';

interface RegisterWebhookModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRegister: (data: { name: string; url: string; env: string; auth: string }) => void;
}

export function RegisterWebhookModal({ isOpen, onClose, onRegister }: RegisterWebhookModalProps) {
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [env, setEnv] = useState('PRODUCTION');
  const [auth, setAuth] = useState('HMAC_SHA256');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !url) {
      alert('Please fill in Endpoint Name and Target URL');
      return;
    }
    onRegister({ name, url, env, auth });
    setName('');
    setUrl('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 font-mono text-xs">
      <div
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md transition-opacity"
        onClick={onClose}
      />

      <div className="relative w-full max-w-lg bg-slate-900 border border-white/[0.1] rounded-2xl shadow-2xl overflow-hidden z-10">
        {/* HEADER */}
        <div className="p-6 border-b border-white/[0.08] flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400">
              <Radio className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider block">
                ZERO-TRUST REGISTRATION
              </span>
              <h3 className="font-display text-base font-bold text-slate-100 mt-0.5">
                REGISTER WEBHOOK ENDPOINT
              </h3>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* FORM */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">
              ENDPOINT NAME
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Finance Operations Webhook Receiver"
              className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2.5 text-xs font-mono text-slate-200 placeholder-slate-600 focus:border-blue-500/40 focus:outline-none"
            />
          </div>

          <div>
            <label className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">
              TARGET URL
            </label>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://api.yourcompany.test/webhooks/receiver"
              className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2.5 text-xs font-mono text-slate-200 placeholder-slate-600 focus:border-blue-500/40 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">
                ENVIRONMENT
              </label>
              <select
                value={env}
                onChange={(e) => setEnv(e.target.value)}
                className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:border-blue-500/40 focus:outline-none"
              >
                <option value="PRODUCTION">PRODUCTION</option>
                <option value="STAGING">STAGING</option>
                <option value="SANDBOX">SANDBOX</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">
                AUTHENTICATION
              </label>
              <select
                value={auth}
                onChange={(e) => setAuth(e.target.value)}
                className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:border-blue-500/40 focus:outline-none"
              >
                <option value="HMAC_SHA256">HMAC_SHA256</option>
                <option value="MTLS">MTLS</option>
                <option value="BEARER_TOKEN">BEARER_TOKEN</option>
                <option value="BASIC_AUTH">BASIC_AUTH</option>
              </select>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-[10px] text-slate-400 space-y-1">
            <div className="text-emerald-400 font-bold flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" /> AUTOMATED SECRET GENERATION
            </div>
            <div>A masked signing secret (whsec_••••••••A91F) will be generated upon registration.</div>
          </div>

          {/* ACTIONS */}
          <div className="pt-2 flex items-center justify-end gap-2">
            <AGButton variant="ghost" size="sm" type="button" onClick={onClose}>
              CANCEL
            </AGButton>
            <AGButton variant="primary" size="sm" type="submit">
              REGISTER ENDPOINT
            </AGButton>
          </div>
        </form>
      </div>
    </div>
  );
}
