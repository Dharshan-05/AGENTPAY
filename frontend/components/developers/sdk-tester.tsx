'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { SdkTestRequest, SdkTestResponse } from './developers-types';
import { Terminal, Play, Copy, Check, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

export function SdkTester() {
  const [agentId, setAgentId] = useState('AGT-892');
  const [amount, setAmount] = useState('2480.00');
  const [merchant, setMerchant] = useState('Acme Hardware Corp');
  const [category, setCategory] = useState('HARDWARE');
  const [response, setResponse] = useState<SdkTestResponse | null>(null);
  const [activeCodeLang, setActiveCodeLang] = useState<'JS' | 'PY' | 'CURL'>('JS');

  const handleRunTest = () => {
    setResponse({
      requestId: `req_${Math.random().toString(36).substring(2, 9)}`,
      agentId,
      decision: 'AUTHORIZED',
      riskScore: 0.08,
      policy: 'AGP-GOV-001',
      fraudGuard: 'LOW RISK',
      execution: 'SANDBOX DEMO EXECUTION',
      latency: '84ms',
      txnHash: '0x9F4AC8102E3B881900281F7A9B8411',
      timestamp: `${new Date().toISOString().substring(11, 19)} UTC`,
    });
  };

  return (
    <div className="space-y-6 font-mono text-xs max-w-4xl">
      <AGCard className="space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Terminal className="w-5 h-5 text-blue-400" /> SDK INTERACTIVE TESTER
            </h3>
            <p className="text-[10px] text-slate-400">Test autonomous payment authorization requests without real money movement</p>
          </div>
          <AGBadge status="REVIEW" label="SANDBOX / DEMO EXECUTION" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          
          {/* INPUT FORM */}
          <div className="space-y-3 p-4 rounded-xl bg-slate-950/80 border border-white/[0.06]">
            <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
              INTENT PARAMETERS BUILDER
            </h4>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[10px] text-slate-400 uppercase mb-1">Target Agent Persona</label>
                <input
                  type="text"
                  value={agentId}
                  onChange={(e) => setAgentId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
                />
              </div>

              <div>
                <label className="block text-[10px] text-slate-400 uppercase mb-1">Intent Amount ($)</label>
                <input
                  type="text"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-emerald-400 font-bold focus:outline-none focus:border-blue-500/50"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[10px] text-slate-400 uppercase mb-1">Merchant Target</label>
                <input
                  type="text"
                  value={merchant}
                  onChange={(e) => setMerchant(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500/50"
                />
              </div>

              <div>
                <label className="block text-[10px] text-slate-400 uppercase mb-1">MCC Category</label>
                <input
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500/50"
                />
              </div>
            </div>

            <div className="pt-2">
              <AGButton variant="primary" size="md" icon={Play} onClick={handleRunTest} className="w-full justify-center">
                RUN AUTHORIZATION TEST
              </AGButton>
            </div>
          </div>

          {/* RESPONSE OUTPUT */}
          <div className="space-y-3 p-4 rounded-xl bg-slate-950 border border-white/[0.08]">
            <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider flex items-center justify-between">
              <span>RESPONSE PAYLOAD (JSON)</span>
              {response && <span className="text-emerald-400 font-bold">200 OK · {response.latency}</span>}
            </h4>

            {response ? (
              <pre className="p-3.5 rounded-xl bg-slate-900 border border-white/[0.06] text-emerald-400 text-[10px] h-48 overflow-y-auto leading-relaxed">
                {JSON.stringify(response, null, 2)}
              </pre>
            ) : (
              <div className="h-48 rounded-xl bg-slate-900 border border-white/[0.04] p-6 flex items-center justify-center text-slate-500 text-center">
                Click "RUN AUTHORIZATION TEST" to simulate SDK intent execution.
              </div>
            )}
          </div>

        </div>
      </AGCard>

      {/* CODE EXAMPLES */}
      <AGCard className="space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-white/[0.08]">
          <span className="font-bold text-slate-100 text-xs">SDK QUICKSTART EXAMPLES</span>
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-white/10 text-[10px]">
            {(['JS', 'PY', 'CURL'] as const).map((lang) => (
              <button
                key={lang}
                onClick={() => setActiveCodeLang(lang)}
                className={`px-3 py-1 rounded-lg font-bold transition-all ${
                  activeCodeLang === lang
                    ? 'bg-blue-500 text-white shadow-[0_0_10px_rgba(59,130,246,0.3)]'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {lang}
              </button>
            ))}
          </div>
        </div>

        <pre className="p-4 rounded-xl bg-slate-950 border border-white/[0.06] text-slate-300 text-[11px] overflow-x-auto leading-relaxed">
          {activeCodeLang === 'JS' && `import { AgentPay } from '@agentpay/sdk';

const agentPay = new AgentPay({ apiKey: process.env.AGENTPAY_API_KEY });
const auth = await agentPay.authorizeIntent({
  agentId: '${agentId}',
  amount: ${amount},
  currency: 'USD',
  merchant: '${merchant}',
});
console.log('Status:', auth.decision); // "AUTHORIZED"`}

          {activeCodeLang === 'PY' && `from agentpay import AgentPay

client = AgentPay(api_key="ag_live_9981a7b")
response = client.authorize_intent(
    agent_id="${agentId}",
    amount=${amount},
    currency="USD",
    merchant="${merchant}"
)
print("Decision:", response.decision)`}

          {activeCodeLang === 'CURL' && `curl -X POST https://api.agentpay.io/v1/payments/authorize \\
  -H "Authorization: Bearer ag_live_9981a7b" \\
  -H "Content-Type: application/json" \\
  -d '{
    "agent_id": "${agentId}",
    "amount": ${amount},
    "currency": "USD",
    "merchant": "${merchant}"
  }'`}
        </pre>
      </AGCard>
    </div>
  );
}
