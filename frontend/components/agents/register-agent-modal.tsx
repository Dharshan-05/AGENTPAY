'use client';

import { AGButton } from '@/components/ui/ag-button';
import { Bot, X, Check } from 'lucide-react';
import { useState } from 'react';

interface RegisterAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRegisterSuccess: (agentName: string, agentType: string) => void;
}

export function RegisterAgentModal({ isOpen, onClose, onRegisterSuccess }: RegisterAgentModalProps) {
  const [name, setName] = useState('');
  const [type, setType] = useState('AUTONOMOUS');
  const [owner, setOwner] = useState('Finance Operations');
  const [environment, setEnvironment] = useState('PRODUCTION');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    onRegisterSuccess(name, type);
    setName('');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4 font-mono">
      <div className="w-full max-w-lg bg-slate-900 border border-white/10 rounded-2xl p-6 shadow-2xl space-y-6 text-xs text-slate-200">
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-blue-400" />
            <h3 className="font-bold text-slate-100 text-sm">REGISTER ZERO-TRUST AGENT IDENTITY</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-slate-800 text-slate-400">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[10px] text-slate-400 font-bold uppercase">AGENT PERSONA NAME</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Treasury Payout Dispatcher Bot"
              required
              className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500/50"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-[10px] text-slate-400 font-bold uppercase">EXECUTION TYPE</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500/50"
              >
                <option value="AUTONOMOUS">AUTONOMOUS</option>
                <option value="SUPERVISED">SUPERVISED</option>
                <option value="WORKFLOW">WORKFLOW</option>
                <option value="SERVICE">SERVICE</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] text-slate-400 font-bold uppercase">ENVIRONMENT</label>
              <select
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500/50"
              >
                <option value="PRODUCTION">PRODUCTION</option>
                <option value="STAGING">STAGING</option>
                <option value="SANDBOX">SANDBOX</option>
              </select>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/30 text-[10px] text-blue-300">
            <span className="font-bold">ZERO-TRUST PROVISIONING:</span> Automated mTLS certificate pair and AGENTGUARD policy binding (<strong className="text-white">AGP-GOV-001</strong>) will be generated upon registration.
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <AGButton variant="ghost" size="sm" type="button" onClick={onClose}>
              CANCEL
            </AGButton>
            <AGButton variant="primary" size="sm" type="submit">
              REGISTER IDENTITY
            </AGButton>
          </div>
        </form>
      </div>
    </div>
  );
}
