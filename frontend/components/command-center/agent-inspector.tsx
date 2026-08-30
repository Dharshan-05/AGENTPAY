'use client';

import { AgentItem } from './agent-fleet';
import {
  X,
  Shield,
  Bot,
  Key,
  Sliders,
  AlertOctagon,
  CheckCircle2,
  Lock,
  History,
  Activity,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface AgentInspectorProps {
  agent: AgentItem | null;
  onClose: () => void;
  onUpdateLimit: (agentId: string, newLimit: number) => void;
  onToggleStatus: (agentId: string) => void;
}

export function AgentInspector({
  agent,
  onClose,
  onUpdateLimit,
  onToggleStatus,
}: AgentInspectorProps) {
  if (!agent) return null;

  const usagePercent = Math.min(100, Math.round((agent.dailySpend / agent.dailyLimit) * 100));

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Dark Overlay Backdrop */}
      <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" onClick={onClose} />

      {/* Slide-over Drawer Container */}
      <div className="relative w-full max-w-md bg-slate-950 border-l border-white/[0.08] h-full shadow-2xl p-6 overflow-y-auto space-y-6 z-10 font-mono">
        
        {/* Header Bar */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-slate-950 font-bold"
              style={{ backgroundColor: agent.color }}
            >
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-display font-bold text-base text-slate-100">{agent.name}</h3>
              <span className="text-[10px] text-slate-400 block">{agent.id}</span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-200 hover:bg-slate-900 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Status & Tier */}
        <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] text-xs">
          <div>
            <span className="text-slate-500 text-[10px] block">SECURITY TIER</span>
            <span className="font-bold text-slate-200">{agent.tier}</span>
          </div>
          <Badge variant={agent.status} />
        </div>

        {/* Financial Capabilities & Policies */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-slate-300 flex items-center gap-2">
            <Lock className="w-3.5 h-3.5 text-emerald-400" /> ACTIVE FINANCIAL GOVERNANCE
          </h4>
          
          <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Rule Policy:</span>
              <span className="text-emerald-400 font-bold">{agent.activePolicy}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Public Key Fingerprint:</span>
              <span className="text-slate-300 font-bold text-[10px]">0x9F4A...892</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Virtual Card Token:</span>
              <span className="text-blue-400 font-bold text-[10px]">●●●● 4920 (SINGLE-USE)</span>
            </div>
          </div>
        </div>

        {/* Spend Limit Controls */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-300 flex items-center gap-2">
              <Sliders className="w-3.5 h-3.5 text-emerald-400" /> DAILY SPEND CAP GOVERNANCE
            </h4>
            <span className="text-[10px] text-slate-400 font-bold">
              ${agent.dailySpend.toLocaleString()} / ${agent.dailyLimit.toLocaleString()}
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-3">
            <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full transition-all duration-500"
                style={{ width: `${usagePercent}%` }}
              />
            </div>

            <div className="flex items-center gap-2 pt-1">
              <Button
                variant="obsidian"
                size="sm"
                className="flex-1"
                onClick={() => onUpdateLimit(agent.id, Math.max(500, agent.dailyLimit - 1000))}
              >
                -$1,000 Limit
              </Button>
              <Button
                variant="obsidian"
                size="sm"
                className="flex-1"
                onClick={() => onUpdateLimit(agent.id, agent.dailyLimit + 1000)}
              >
                +$1,000 Limit
              </Button>
            </div>
          </div>
        </div>

        {/* Recent Audit Trail */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-slate-300 flex items-center gap-2">
            <History className="w-3.5 h-3.5 text-emerald-400" /> RECENT AUDIT EVENT
          </h4>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] text-xs">
            <p className="text-slate-300 font-sans leading-relaxed">{agent.lastAction}</p>
            <span className="text-[10px] text-slate-500 block mt-2">Verified via Cryptographic Proof</span>
          </div>
        </div>

        {/* Security Override Actions */}
        <div className="space-y-2 pt-4 border-t border-white/[0.08]">
          <Button
            variant={agent.status === 'SUSPENDED' ? 'emerald' : 'danger'}
            size="md"
            className="w-full"
            onClick={() => onToggleStatus(agent.id)}
          >
            <AlertOctagon className="w-4 h-4 mr-2" />
            {agent.status === 'SUSPENDED' ? 'REACTIVATE AGENT PERMISSIONS' : 'SUSPEND AGENT PERMISSIONS'}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            className="w-full text-slate-400"
            onClick={() => alert(`Audit log generated for ${agent.id}`)}
          >
            Export Audit Trail (JSON)
          </Button>
        </div>

      </div>
    </div>
  );
}
