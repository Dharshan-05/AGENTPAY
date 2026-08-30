'use client';

import { useState } from 'react';
import { AGButton } from '@/components/ui/ag-button';
import { X, CreditCard, ShieldCheck } from 'lucide-react';
import { InstrumentType } from './payment-method-types';

interface RegisterPaymentMethodModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (data: { name: string; type: InstrumentType; env: string; currency: string; country: string; agent: string; processor: string }) => void;
}

export function RegisterPaymentMethodModal({ isOpen, onClose, onAdd }: RegisterPaymentMethodModalProps) {
  const [name, setName] = useState('');
  const [type, setType] = useState<InstrumentType>('CARD');
  const [env, setEnv] = useState('PRODUCTION');
  const [currency, setCurrency] = useState('USD');
  const [country, setCountry] = useState('US');
  const [agent, setAgent] = useState('AGT-892');
  const [processor, setProcessor] = useState('Stripe');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) {
      alert('Please fill in Instrument Display Name');
      return;
    }
    onAdd({ name, type, env, currency, country, agent, processor });
    setName('');
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
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider block">
                ZERO-TRUST PCI REGISTER
              </span>
              <h3 className="font-display text-base font-bold text-slate-100 mt-0.5">
                ADD PAYMENT INSTRUMENT
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
              INSTRUMENT NAME
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Procurement Corporate Visa Vault"
              className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2.5 text-xs font-mono text-slate-200 placeholder-slate-600 focus:border-blue-500/40 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">
                INSTRUMENT TYPE
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as InstrumentType)}
                className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:border-blue-500/40 focus:outline-none"
              >
                <option value="CARD">CARD</option>
                <option value="VIRTUAL_CARD">VIRTUAL_CARD</option>
                <option value="BANK_ACCOUNT">BANK_ACCOUNT</option>
                <option value="UPI">UPI</option>
                <option value="WALLET">WALLET</option>
                <option value="BANK_TRANSFER">BANK_TRANSFER</option>
                <option value="TOKENIZED_CARD">TOKENIZED_CARD</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">
                PROCESSOR
              </label>
              <select
                value={processor}
                onChange={(e) => setProcessor(e.target.value)}
                className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:border-blue-500/40 focus:outline-none"
              >
                <option value="Stripe">Stripe</option>
                <option value="Adyen">Adyen</option>
                <option value="JPMorgan Direct">JPMorgan Direct</option>
                <option value="Citibank Direct">Citibank Direct</option>
                <option value="Razorpay">Razorpay</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">
                ENV
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
                COUNTRY
              </label>
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:border-blue-500/40 focus:outline-none"
              >
                <option value="US">US</option>
                <option value="DE">DE</option>
                <option value="GB">GB</option>
                <option value="IN">IN</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">
                CURRENCY
              </label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:border-blue-500/40 focus:outline-none"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="INR">INR</option>
              </select>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-[10px] text-slate-400 space-y-1">
            <div className="text-emerald-400 font-bold flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" /> EMVCo NETWORK TOKENIZATION
            </div>
            <div>A masked instrument identifier and network token (tok_ntk_9901X) will be assigned.</div>
          </div>

          {/* ACTIONS */}
          <div className="pt-2 flex items-center justify-end gap-2">
            <AGButton variant="ghost" size="sm" type="button" onClick={onClose}>
              CANCEL
            </AGButton>
            <AGButton variant="primary" size="sm" type="submit">
              ADD PAYMENT METHOD
            </AGButton>
          </div>
        </form>
      </div>
    </div>
  );
}
