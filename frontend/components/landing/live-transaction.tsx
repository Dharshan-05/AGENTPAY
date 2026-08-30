'use client';

import { useState } from 'react';
import { Reveal } from '@/components/motion/reveal';
import { ShieldCheck, Terminal, Play, RotateCcw, CheckCircle2, AlertTriangle, Lock } from 'lucide-react';

export function LiveTransaction() {
  const [amount, setAmount] = useState(2480);
  const [vendor, setVendor] = useState('Electronics Distributor Inc.');
  const [agentType, setAgentType] = useState('Shopping Agent #402');
  const [simulating, setSimulating] = useState(false);
  const [logs, setLogs] = useState<string[]>([
    '[00:32:01] AGENTPAY daemon started. Listening for incoming agent payload...',
    '[00:32:02] Received payload from Shopping Agent #402: Purchase $2,480 electronics.',
    '[00:32:02] AGENTGUARD Policy Engine: Limit check passed ($2,480 <= $5,000 max daily).',
    '[00:32:03] FRAUDGUARD AI Engine: Intent vector clean. Anomaly score: 0.08 (Low Risk).',
    '[00:32:03] Decision: AUTHORIZED. VirtCard generated. Settlement: COMPLETED.',
  ]);

  const riskScore = amount > 4500 ? 0.76 : 0.08;
  const isHighRisk = riskScore > 0.4;

  function runSimulation() {
    setSimulating(true);
    setLogs((prev) => [
      `[${new Date().toLocaleTimeString()}] INITIATING MANUAL TELEMETRY TEST...`,
      `[${new Date().toLocaleTimeString()}] Agent: ${agentType} | Intent: Purchase $${amount} from ${vendor}`,
      `[${new Date().toLocaleTimeString()}] AGENTGUARD Policy check... ${amount > 5000 ? 'FAILED (Exceeds Limit)' : 'APPROVED'}`,
      `[${new Date().toLocaleTimeString()}] FRAUDGUARD Scanning... Risk Score: ${riskScore.toFixed(2)}`,
      `[${new Date().toLocaleTimeString()}] Decision: ${isHighRisk ? 'ESCALATED TO HUMAN APPROVAL' : 'AUTHORIZED & EXECUTED'}`,
    ]);
    setTimeout(() => setSimulating(false), 800);
  }

  return (
    <section className="py-24 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-6">
        
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Reveal y={12}>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono uppercase tracking-widest mb-3">
              <Terminal className="w-3.5 h-3.5" />
              Live Infrastructure Telemetry
            </div>
          </Reveal>
          <Reveal y={16} delay={0.1}>
            <h2 className="text-3xl sm:text-5xl font-display font-bold text-slate-100 mb-4 tracking-tight">
              LIVE SYSTEM VISUALIZATION
            </h2>
          </Reveal>
          <Reveal y={16} delay={0.2}>
            <p className="text-base text-slate-400 font-sans">
              Test real-time policy evaluation, fraud scoring, and payment execution telemetry.
            </p>
          </Reveal>
        </div>

        {/* Telemetry Console Frame */}
        <Reveal y={20} className="bg-slate-950/90 border border-white/[0.1] rounded-2xl p-6 sm:p-8 backdrop-blur-2xl shadow-2xl">
          
          {/* Header Bar */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-white/[0.08] gap-4 mb-8">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-emerald-500 animate-ping" />
              <span className="text-xs font-mono text-slate-200 font-bold uppercase tracking-wider">
                AGENTPAY TELEMETRY MONITOR // NODE #01-US-EAST
              </span>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={runSimulation}
                disabled={simulating}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-mono text-xs hover:bg-emerald-500/30 transition-all"
              >
                <Play className="w-3.5 h-3.5" />
                {simulating ? 'Evaluating...' : 'Run Simulation'}
              </button>
            </div>
          </div>

          {/* Infrastructure Grid Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-8">
            
            {/* Metric 1: Agent */}
            <div className="bg-slate-900/60 border border-white/[0.08] rounded-xl p-4">
              <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
                Agent Identity
              </span>
              <span className="text-xs font-mono font-bold text-slate-200 block truncate">
                {agentType}
              </span>
              <span className="text-[9px] font-mono text-emerald-400 mt-1 block">
                AUTHENTICATED
              </span>
            </div>

            {/* Metric 2: Intent */}
            <div className="bg-slate-900/60 border border-white/[0.08] rounded-xl p-4">
              <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
                Financial Intent
              </span>
              <span className="text-xs font-mono font-bold text-slate-200 block truncate">
                Purchase ${amount.toLocaleString()} electronics
              </span>
              <span className="text-[9px] font-mono text-slate-400 mt-1 block">
                Target: {vendor}
              </span>
            </div>

            {/* Metric 3: AGENTGUARD */}
            <div className="bg-slate-900/60 border border-white/[0.08] rounded-xl p-4">
              <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
                AGENTGUARD Policy
              </span>
              <span className="text-xs font-mono font-bold text-emerald-400 block flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Approved
              </span>
              <span className="text-[9px] font-mono text-slate-400 mt-1 block">
                Rule set #89-A
              </span>
            </div>

            {/* Metric 4: FRAUDGUARD */}
            <div className="bg-slate-900/60 border border-white/[0.08] rounded-xl p-4">
              <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
                FRAUDGUARD Risk
              </span>
              <span className={`text-xs font-mono font-bold block ${isHighRisk ? 'text-amber-400' : 'text-emerald-400'}`}>
                Risk Score: {riskScore.toFixed(2)}
              </span>
              <span className="text-[9px] font-mono text-slate-400 mt-1 block">
                {isHighRisk ? 'ELEVATED RISK' : 'LOW RISK / CLEAN'}
              </span>
            </div>

            {/* Metric 5: Decision */}
            <div className="bg-slate-900/60 border border-white/[0.08] rounded-xl p-4">
              <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
                System Decision
              </span>
              <span className="text-xs font-mono font-bold text-emerald-400 block tracking-wider">
                {isHighRisk ? 'HUMAN ESCALATION' : 'AUTHORIZED'}
              </span>
              <span className="text-[9px] font-mono text-slate-400 mt-1 block">
                Auto-policy pass
              </span>
            </div>

            {/* Metric 6: Payment */}
            <div className="bg-slate-900/60 border border-white/[0.08] rounded-xl p-4">
              <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
                Payment Status
              </span>
              <span className="text-xs font-mono font-bold text-emerald-400 block tracking-wider">
                COMPLETED
              </span>
              <span className="text-[9px] font-mono text-slate-400 mt-1 block">
                Settled 12ms
              </span>
            </div>

          </div>

          {/* Console Log Stream Box */}
          <div className="bg-slate-900/90 border border-white/[0.08] rounded-xl p-5 font-mono text-xs text-slate-300">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/[0.06] text-[10px] text-slate-500">
              <span className="flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                AUDIT LOG CONSOLE STREAM
              </span>
              <span className="text-emerald-400">REALTIME TELEMETRY</span>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {logs.map((log, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <span className="text-slate-600 select-none">&gt;</span>
                  <span className={log.includes('AUTHORIZED') || log.includes('passed') ? 'text-emerald-400' : 'text-slate-300'}>
                    {log}
                  </span>
                </div>
              ))}
            </div>
          </div>

        </Reveal>

      </div>
    </section>
  );
}
