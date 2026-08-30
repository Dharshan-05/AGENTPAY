'use client';

import { Bot, Shield, AlertTriangle, CheckCircle, Lock, Sliders, ChevronRight } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export interface AgentItem {
  id: string;
  name: string;
  role: string;
  tier: string;
  status: 'ACTIVE' | 'PENDING_APPROVAL' | 'HIGH_RISK' | 'SUSPENDED';
  dailySpend: number;
  dailyLimit: number;
  riskScore: number;
  lastAction: string;
  activePolicy: string;
  color: string;
}

interface AgentFleetProps {
  agents: AgentItem[];
  selectedAgentId: string | null;
  onSelectAgent: (agent: AgentItem) => void;
}

export function AgentFleet({ agents, selectedAgentId, onSelectAgent }: AgentFleetProps) {
  return (
    <div className="space-y-6">
      {/* Roster Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-white/[0.08] gap-2">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-display font-bold text-base text-slate-100 tracking-tight flex items-center gap-2">
              MANAGED AGENT FLEET & TOPOLOGY
              <span className="text-xs font-mono font-normal text-slate-400">({agents.length} AGENTS)</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-400">
              Autonomous Identity & Real-Time Spend Limits
            </span>
          </div>
        </div>

        <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase">
          ● 100% Policy Enforced
        </span>
      </div>

      {/* Roster Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => {
          const isSelected = selectedAgentId === agent.id;
          const usagePercent = Math.min(100, Math.round((agent.dailySpend / agent.dailyLimit) * 100));
          const isNearCap = usagePercent >= 85;

          return (
            <Card
              key={agent.id}
              onClick={() => onSelectAgent(agent)}
              variant={isSelected ? 'glow' : 'default'}
              className="p-5 cursor-pointer group hover:scale-[1.01] transition-transform"
            >
              {/* Top Row: Identity & Status Badge */}
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center text-slate-950 font-bold font-mono shadow-md shrink-0"
                    style={{ backgroundColor: agent.color }}
                  >
                    <Bot className="w-5 h-5 text-slate-950" />
                  </div>
                  <div>
                    <h4 className="font-display font-bold text-sm text-slate-100 group-hover:text-emerald-300 transition-colors">
                      {agent.name}
                    </h4>
                    <span className="text-[10px] font-mono text-slate-400 block truncate max-w-[150px]">
                      {agent.role}
                    </span>
                  </div>
                </div>

                <Badge variant={agent.status} />
              </div>

              {/* Spend Utilization Bar */}
              <div className="space-y-1.5 my-4">
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <span>Spend Utilization</span>
                  <span className={`font-bold ${isNearCap ? 'text-amber-400' : 'text-slate-200'}`}>
                    ${agent.dailySpend.toLocaleString()} / ${agent.dailyLimit.toLocaleString()} ({usagePercent}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden border border-white/[0.06]">
                  <div
                    className={`h-full transition-all duration-500 rounded-full ${
                      isNearCap ? 'bg-amber-400' : 'bg-gradient-to-r from-emerald-500 to-emerald-400'
                    }`}
                    style={{ width: `${usagePercent}%` }}
                  />
                </div>
              </div>

              {/* Bottom Metadata: Policy & Risk */}
              <div className="pt-3 border-t border-white/[0.06] flex items-center justify-between text-[10px] font-mono">
                <div className="flex items-center gap-1.5 text-slate-400">
                  <Lock className="w-3 h-3 text-emerald-400" />
                  <span className="truncate max-w-[120px]">{agent.activePolicy}</span>
                </div>

                <div className="flex items-center gap-1">
                  <span className="text-slate-500">Risk:</span>
                  <span
                    className={`font-bold px-1.5 py-0.5 rounded ${
                      agent.riskScore > 0.4 ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
                    }`}
                  >
                    {agent.riskScore.toFixed(2)} ({agent.riskScore > 0.4 ? 'HIGH' : 'LOW'})
                  </span>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-slate-200 transition-colors" />
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
