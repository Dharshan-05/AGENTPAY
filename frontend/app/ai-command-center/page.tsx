'use client';

import { useState } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGCard, AGMetricCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { Terminal, Bot, Sparkles, Send, Cpu, Activity, Brain } from 'lucide-react';

export default function AiCommandCenterPage() {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<
    { role: 'user' | 'assistant'; text: string; time: string }[]
  >([
    {
      role: 'assistant',
      text: 'AI Command Center active. Model: AGENT-INTELLIGENCE v3.2. Ready for natural language payment orchestration and intent parsing.',
      time: '02:04:18 UTC',
    },
  ]);

  const handleSend = () => {
    if (!prompt.trim()) return;
    const userMsg = { role: 'user' as const, text: prompt, time: new Date().toLocaleTimeString() };
    const aiMsg = {
      role: 'assistant' as const,
      text: `Parsed Intent: Authorize purchase for "${prompt}". Executing zero-trust policy check against AGP-GOV-001... Status: AUTHORIZED.`,
      time: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMsg, aiMsg]);
    setPrompt('');
  };

  return (
    <AgentPayShell activeTab="ai-command-center">
      <div className="space-y-6">
        <PageHeader
          eyebrow="NATURAL LANGUAGE ORCHESTRATION"
          title="AI COMMAND"
          highlightTitle="CENTER"
          description="Natural language agent command interface, intent parsing, real-time prompt security, and neural decision trees."
          icon={Terminal}
          statusBadge={<AGBadge status="LIVE" label="NEURAL ROUTER ACTIVE" />}
          actions={
            <>
              <AGButton variant="primary" icon={Sparkles}>
                Parse Intent
              </AGButton>
              <AGButton variant="secondary" icon={Brain}>
                Model Benchmarks
              </AGButton>
            </>
          }
        />

        {/* Intelligence KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="NEURAL INTENTS" value="14,890" trend="+24.1%" subtext="Parsed Natural Language Requests" />
          <AGMetricCard label="PARSING LATENCY" value="18ms" trend="-3ms" subtext="Real-time Semantic Router" />
          <AGMetricCard label="INTENT ACCURACY" value="99.4%" trend="Optimal" subtext="Zero Ambiguity Execution" />
          <AGMetricCard label="PROMPT SHIELDS" value="142 Blocked" subtext="Adversarial Injection Defended" />
        </div>

        {/* AI Command Interface Terminal */}
        <AGCard className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] font-mono text-xs">
            <span className="font-bold text-slate-100 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-purple-400" /> NEURAL AGENT INTERACTION TERMINAL
            </span>
            <AGBadge status="ACTIVE" label="AGENTPAY-LLM v3.2" />
          </div>

          <div className="h-80 rounded-xl bg-slate-950/90 border border-white/[0.06] p-4 font-mono text-xs overflow-y-auto space-y-3">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`p-3 rounded-xl max-w-2xl text-xs space-y-1 ${
                  m.role === 'assistant'
                    ? 'bg-blue-500/10 border border-blue-500/20 text-slate-200 ml-0'
                    : 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 ml-auto text-right'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] text-slate-400">
                  <span>{m.role === 'assistant' ? 'SYSTEM // NEURAL ROUTER' : 'OPERATOR'}</span>
                  <span>{m.time}</span>
                </div>
                <p className="leading-relaxed">{m.text}</p>
              </div>
            ))}
          </div>

          {/* Prompt Input */}
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type natural language command e.g. 'Authorize Procurement Agent to purchase 4 GPU instances'..."
              className="flex-1 px-4 py-3 bg-slate-950 border border-white/10 rounded-xl text-xs font-mono text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500/50"
            />
            <AGButton variant="primary" icon={Send} onClick={handleSend}>
              Send Intent
            </AGButton>
          </div>
        </AGCard>
      </div>
    </AgentPayShell>
  );
}
