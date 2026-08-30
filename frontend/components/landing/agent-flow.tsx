'use client';

import { useRef, useState, useEffect } from 'react';
import { AnimatedBeam } from '@/components/motion/animated-beam';
import { Bot, FileCode, Shield, Cpu, CheckCircle2, CreditCard, Sparkles, Activity } from 'lucide-react';

export function AgentFlow() {
  const containerRef = useRef<HTMLDivElement>(null);
  const node1Ref = useRef<HTMLDivElement>(null);
  const node2Ref = useRef<HTMLDivElement>(null);
  const node3Ref = useRef<HTMLDivElement>(null);
  const node4Ref = useRef<HTMLDivElement>(null);
  const node5Ref = useRef<HTMLDivElement>(null);
  const node6Ref = useRef<HTMLDivElement>(null);

  const [activeStep, setActiveStep] = useState(0);

  // Pulse animation along steps
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 6);
    }, 2500);
    return () => clearInterval(timer);
  }, []);

  const NODES = [
    {
      id: 'agent',
      ref: node1Ref,
      icon: Bot,
      title: 'Agent Identity',
      badge: 'Autonomous',
      color: '#3B82F6',
      detail: 'Agent #892 (Procurement)',
    },
    {
      id: 'intent',
      ref: node2Ref,
      icon: FileCode,
      title: 'Intent',
      badge: 'Payload',
      color: '#60A5FA',
      detail: 'Purchase $2,480 Server Hardware',
    },
    {
      id: 'agentguard',
      ref: node3Ref,
      icon: Shield,
      title: 'AGENTGUARD',
      badge: 'Policy Governance',
      color: '#10B981',
      detail: 'Spending limit & Merchant policy: PASS',
    },
    {
      id: 'fraudguard',
      ref: node4Ref,
      icon: Cpu,
      title: 'FRAUDGUARD',
      badge: 'AI Risk Engine',
      color: '#6366F1',
      detail: 'Anomalous intent score: 0.08 (Safe)',
    },
    {
      id: 'decision',
      ref: node5Ref,
      icon: CheckCircle2,
      title: 'Decision',
      badge: 'Verified',
      color: '#10B981',
      detail: 'Policy Authorized & Auto-approved',
    },
    {
      id: 'payment',
      ref: node6Ref,
      icon: CreditCard,
      title: 'Payment',
      badge: 'Execution',
      color: '#34D399',
      detail: 'Atomic settlement executed',
    },
  ];

  return (
    <div
      ref={containerRef}
      className="relative w-full rounded-2xl bg-slate-950/80 border border-white/[0.08] p-6 md:p-8 backdrop-blur-xl shadow-2xl overflow-hidden"
    >
      {/* Background Grid Lines & Telemetry Header */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />
      
      <div className="flex items-center justify-between border-b border-white/[0.06] pb-4 mb-8">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
          </div>
          <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            AgentPay Infrastructure Telemetry Pipeline
          </span>
        </div>
        <div className="hidden sm:flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-[10px] font-mono text-emerald-400/90 uppercase tracking-wider">
            Live Verification Active
          </span>
        </div>
      </div>

      {/* SVG Beams Connecting Nodes in Sequence */}
      <AnimatedBeam containerRef={containerRef} fromRef={node1Ref} toRef={node2Ref} fromColor="#3B82F6" toColor="#60A5FA" duration={2.5} />
      <AnimatedBeam containerRef={containerRef} fromRef={node2Ref} toRef={node3Ref} fromColor="#60A5FA" toColor="#10B981" duration={2.5} />
      <AnimatedBeam containerRef={containerRef} fromRef={node3Ref} toRef={node4Ref} fromColor="#10B981" toColor="#6366F1" duration={2.5} />
      <AnimatedBeam containerRef={containerRef} fromRef={node4Ref} toRef={node5Ref} fromColor="#6366F1" toColor="#10B981" duration={2.5} />
      <AnimatedBeam containerRef={containerRef} fromRef={node5Ref} toRef={node6Ref} fromColor="#10B981" toColor="#34D399" duration={2.5} />

      {/* Node Grid Layout */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 relative z-10">
        {NODES.map((node, index) => {
          const Icon = node.icon;
          const isActive = activeStep === index;
          return (
            <div
              key={node.id}
              ref={node.ref}
              onClick={() => setActiveStep(index)}
              className={`cursor-pointer group relative p-4 rounded-xl border transition-all duration-300 ${
                isActive
                  ? 'bg-slate-900/90 border-emerald-500/50 shadow-[0_0_25px_rgba(16,185,129,0.2)] scale-[1.02]'
                  : 'bg-slate-900/40 border-white/[0.08] hover:border-white/20 hover:bg-slate-900/60'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${
                    isActive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/[0.05] text-slate-400 group-hover:text-slate-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-[9px] font-mono tracking-wider px-2 py-0.5 rounded-full bg-white/[0.06] text-slate-400 uppercase">
                  {node.badge}
                </span>
              </div>
              
              <h4 className="text-xs font-mono font-bold text-slate-200 mb-1 flex items-center justify-between">
                {node.title}
                {isActive && <Sparkles className="w-3 h-3 text-emerald-400 animate-spin" />}
              </h4>
              <p className="text-[10px] font-sans text-slate-400 leading-snug line-clamp-2">
                {node.detail}
              </p>
            </div>
          );
        })}
      </div>

      {/* Flow Execution Summary Line */}
      <div className="mt-8 pt-4 border-t border-white/[0.06] flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] font-mono text-slate-400">
        <div className="flex items-center gap-2">
          <span className="text-emerald-400 font-bold">STATUS:</span>
          <span className="text-slate-200">Zero-Trust Authorization Passed</span>
        </div>
        <div className="flex items-center gap-4 text-[10px] text-slate-400">
          <span>Latency: <strong className="text-slate-200">14ms</strong></span>
          <span>Cryptographic Proof: <strong className="text-emerald-400 font-mono">0x9F4A...8C1D</strong></span>
        </div>
      </div>
    </div>
  );
}
