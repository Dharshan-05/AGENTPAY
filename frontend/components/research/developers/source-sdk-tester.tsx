'use client';

import { Terminal, Play, CheckCircle2 } from 'lucide-react';
import { useState } from 'react';

export function SourceSdkTester() {
  const [agentId, setAgentId] = useState('AGT-892');
  const [amount, setAmount] = useState('2480.00');
  const [merchant, setMerchant] = useState('Acme Hardware');
  const [response, setResponse] = useState<string | null>(null);

  const handleRunTest = () => {
    setResponse(JSON.stringify({
      status: 'AUTHORIZED',
      authorizationId: `auth_${Math.random().toString(36).substring(2, 9)}`,
      agentId,
      amount: `$${amount}`,
      merchant,
      policyResult: 'PASSED (AGP-GOV-001)',
      riskScore: 0.08,
      timestamp: new Date().toISOString(),
    }, null, 2));
  };

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800 max-w-4xl">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Terminal className="w-4 h-4 text-blue-600" />
            Interactive SDK Integration & Intent Authorization Tester
          </h3>
          <p className="text-xs text-slate-500">Excavated interactive API playground architecture</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* INPUTS */}
        <div className="space-y-3 font-mono">
          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-500 mb-1">Target Agent ID</label>
            <input
              type="text"
              value={agentId}
              onChange={(e) => setAgentId(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-bold focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-500 mb-1">Intent Spend Amount ($)</label>
            <input
              type="text"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-bold focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-500 mb-1">Merchant Target</label>
            <input
              type="text"
              value={merchant}
              onChange={(e) => setMerchant(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-bold focus:outline-none focus:border-blue-500"
            />
          </div>

          <button
            onClick={handleRunTest}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl flex items-center justify-center gap-1.5 transition-colors font-sans"
          >
            <Play className="w-4 h-4" /> Run Intent Authorization Test
          </button>
        </div>

        {/* RESPONSE JSON */}
        <div className="space-y-2 font-mono">
          <span className="text-[10px] uppercase font-bold text-slate-500 block">API Response Payload</span>
          <pre className="p-3.5 bg-slate-900 text-emerald-400 rounded-xl border border-slate-800 text-[11px] h-52 overflow-y-auto leading-relaxed">
            {response || '// Click "Run Intent Authorization Test" to simulate SDK payload execution.'}
          </pre>
        </div>
      </div>
    </div>
  );
}
