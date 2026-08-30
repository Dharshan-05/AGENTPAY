'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { ExternalLink, Play, CheckCircle2, Shield } from 'lucide-react';
import { useState } from 'react';

export function CheckoutTester() {
  const [amount, setAmount] = useState<string>('2480.00');
  const [currency, setCurrency] = useState<string>('USD');
  const [customer, setCustomer] = useState<string>('Acme Procurement Inc');
  const [merchant, setMerchant] = useState<string>('Acme Hardware Corp');
  const [generatedSessionId, setGeneratedSessionId] = useState<string | null>(null);

  const handleCreateSession = () => {
    setGeneratedSessionId(`cs_live_${Math.random().toString(36).substring(2, 10)}`);
  };

  return (
    <div className="space-y-6 font-mono text-xs max-w-3xl">
      <AGCard className="space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
          <div>
            <h3 className="text-base font-bold text-slate-100">CHECKOUT SESSION TESTER</h3>
            <p className="text-[10px] text-slate-400">Generate and test hosted payment intent checkout sessions</p>
          </div>
          <AGBadge status="REVIEW" label="SANDBOX EXECUTION" />
        </div>

        <div className="space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
                Customer Name
              </label>
              <input
                type="text"
                value={customer}
                onChange={(e) => setCustomer(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-emerald-500/50"
              />
            </div>

            <div>
              <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
                Merchant Target
              </label>
              <input
                type="text"
                value={merchant}
                onChange={(e) => setMerchant(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-emerald-500/50"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
                Payment Amount ($)
              </label>
              <input
                type="text"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold text-emerald-400 focus:outline-none focus:border-emerald-500/50"
              />
            </div>

            <div>
              <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
                Currency
              </label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-emerald-500/50"
              >
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
          </div>

          <div className="pt-2">
            <AGButton variant="primary" size="md" icon={Play} onClick={handleCreateSession} className="w-full justify-center">
              CREATE TEST CHECKOUT SESSION
            </AGButton>
          </div>

          {generatedSessionId && (
            <div className="p-4 rounded-xl bg-slate-950 border border-emerald-500/30 space-y-2">
              <div className="flex justify-between items-center text-emerald-400 font-bold">
                <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4" /> SESSION CREATED</span>
                <span>ID: {generatedSessionId}</span>
              </div>
              <p className="text-[10px] text-slate-400">
                Generated Checkout URL: <span className="text-blue-400 font-bold">https://checkout.agentpay.io/session/{generatedSessionId}</span>
              </p>
            </div>
          )}
        </div>
      </AGCard>
    </div>
  );
}
