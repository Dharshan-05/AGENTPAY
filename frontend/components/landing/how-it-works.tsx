'use client';

import { useState } from 'react';
import { Reveal } from '@/components/motion/reveal';
import { FileText, Key, ShieldCheck, AlertCircle, UserCheck, CreditCard, History, ChevronRight } from 'lucide-react';

const STEPS = [
  {
    id: 'intent',
    number: '01',
    title: 'Intent',
    icon: FileText,
    headline: 'Agent Expresses Financial Intent',
    desc: 'The autonomous AI agent emits a structured intent payload detailing purchase target, amount, vendor, and business justification.',
    code: `{
  "agent_id": "agent_procure_99",
  "intent": "purchase_cloud_server",
  "amount": 2480.00,
  "currency": "USD",
  "vendor": "AWS infrastructure",
  "justification": "Auto-scaling GPU cluster for batch job"
}`,
  },
  {
    id: 'identity',
    number: '02',
    title: 'Identity Verification',
    icon: Key,
    headline: 'Cryptographic Agent Authentication',
    desc: 'AGENTPAY validates the agent’s cryptographic key, verifying public identity, owner organization, and session signatures.',
    code: `{
  "identity_status": "VERIFIED",
  "key_fingerprint": "SHA256:7f8a9b...",
  "owner_org": "Acme Corp Enterprise",
  "trust_level": "TIER_1_AUTONOMOUS"
}`,
  },
  {
    id: 'policy',
    number: '03',
    title: 'AGENTGUARD Policy Check',
    icon: ShieldCheck,
    headline: 'Deterministic Rule Engine Evaluation',
    desc: 'Evaluates spend against daily limits ($5,000 max), merchant category whitelists, and current organizational approval policies.',
    code: `{
  "policy_id": "pol_daily_infra_v2",
  "rule_evaluations": [
    { "rule": "daily_limit_under_5000", "result": "PASS" },
    { "rule": "vendor_whitelisted", "result": "PASS" }
  ],
  "governance": "APPROVED"
}`,
  },
  {
    id: 'risk',
    number: '04',
    title: 'FRAUDGUARD Risk Scoring',
    icon: AlertCircle,
    headline: 'AI Contextual Anomaly Scan',
    desc: 'Analyzes intent for prompt injection patterns, agent loop hallucination, velocity spikes, and supplier fraud risk.',
    code: `{
  "fraudguard_risk_score": 0.08,
  "risk_category": "LOW_RISK",
  "prompt_injection_detected": false,
  "velocity_anomaly": false,
  "recommendation": "EXECUTE_IMMEDIATELY"
}`,
  },
  {
    id: 'approval',
    number: '05',
    title: 'Human Approval (If Required)',
    icon: UserCheck,
    headline: 'Human-in-the-Loop Safeguard',
    desc: 'If risk exceeds policy threshold or amount surpasses autonomous limits, AGENTPAY routes a quick-action request to human admins.',
    code: `{
  "hitl_status": "SKIPPED_AUTO_APPROVED",
  "reason": "Risk score (0.08) < Threshold (0.40)",
  "escalation_target": "finance-admin@acme.com"
}`,
  },
  {
    id: 'payment',
    number: '06',
    title: 'Payment Execution',
    icon: CreditCard,
    headline: 'Atomic Financial Settlement',
    desc: 'Generates single-use virtual card credentials or executes direct bank API transfer bound specifically to the approved payload.',
    code: `{
  "payment_id": "pay_901238491",
  "method": "VIRTUAL_CARD_SINGLE_USE",
  "status": "COMPLETED",
  "settlement_timestamp": "2026-08-30T00:32:00Z"
}`,
  },
  {
    id: 'audit',
    number: '07',
    title: 'Audit & Telemetry',
    icon: History,
    headline: 'Immutable Explainable Record',
    desc: 'Generates an end-to-end cryptographic audit trail linking prompt, intent, policy decisions, risk vectors, and payment receipt.',
    code: `{
  "audit_hash": "0x4a8f9c1d2e3b...",
  "explainability": "Purchased authorized server capacity within budget.",
  "ledger_logged": true
}`,
  },
];

export function HowItWorks() {
  const [activeStep, setActiveStep] = useState(0);
  const current = STEPS[activeStep];
  const Icon = current.icon;

  return (
    <section className="py-24 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-6">
        
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Reveal y={12}>
            <p className="text-[11px] font-mono tracking-[0.25em] text-emerald-400 uppercase mb-3">
              Step-by-Step Flow
            </p>
          </Reveal>
          <Reveal y={16} delay={0.1}>
            <h2 className="text-3xl sm:text-5xl font-display font-bold text-slate-100 mb-6 tracking-tight">
              HOW IT WORKS
            </h2>
          </Reveal>
          <Reveal y={16} delay={0.2}>
            <p className="text-base text-slate-400 font-sans">
              From raw agent intent to verified payment settlement in milliseconds.
            </p>
          </Reveal>
        </div>

        {/* Step Tabs Navigation */}
        <div className="flex items-center gap-2 overflow-x-auto pb-4 mb-8 scrollbar-none">
          {STEPS.map((step, idx) => (
            <button
              key={step.id}
              onClick={() => setActiveStep(idx)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-mono text-xs whitespace-nowrap border transition-all ${
                activeStep === idx
                  ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.2)]'
                  : 'bg-slate-900/40 border-white/[0.08] text-slate-400 hover:text-slate-200 hover:border-white/20'
              }`}
            >
              <span className="text-[10px] opacity-70">{step.number}</span>
              <span>{step.title}</span>
              {idx < STEPS.length - 1 && <ChevronRight className="w-3 h-3 text-slate-600 ml-1 hidden sm:inline" />}
            </button>
          ))}
        </div>

        {/* Active Step Interactive Showcase Box */}
        <Reveal key={current.id} y={16} className="grid grid-cols-1 lg:grid-cols-12 gap-8 bg-slate-950/80 border border-white/[0.08] rounded-2xl p-8 backdrop-blur-xl">
          <div className="lg:col-span-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <span className="text-[11px] font-mono text-emerald-400 uppercase tracking-widest">
                    Step {current.number} Pipeline Phase
                  </span>
                  <h3 className="text-2xl font-display font-bold text-slate-100">
                    {current.headline}
                  </h3>
                </div>
              </div>

              <p className="text-sm text-slate-300 leading-relaxed font-sans mb-8">
                {current.desc}
              </p>
            </div>

            <div className="flex items-center justify-between border-t border-white/[0.06] pt-4 text-xs font-mono text-slate-400">
              <span>ACTIVE ENGINE: {current.id.toUpperCase()}</span>
              <button
                onClick={() => setActiveStep((activeStep + 1) % STEPS.length)}
                className="text-emerald-400 hover:underline flex items-center gap-1"
              >
                Next Phase <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Live Code/Telemetry Inspector */}
          <div className="lg:col-span-6 bg-slate-900/90 border border-white/[0.08] rounded-xl p-5 font-mono text-xs text-slate-300 overflow-x-auto shadow-inner">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/[0.06] text-[10px] text-slate-500">
              <span>TELEMETRY PAYLOAD SNAPSHOT</span>
              <span className="text-emerald-400">JSON SCHEMA VERIFIED</span>
            </div>
            <pre className="text-emerald-400/90 leading-relaxed font-mono">
              <code>{current.code}</code>
            </pre>
          </div>
        </Reveal>

      </div>
    </section>
  );
}
