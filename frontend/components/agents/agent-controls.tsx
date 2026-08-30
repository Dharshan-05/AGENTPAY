'use client';

import { AGButton } from '@/components/ui/ag-button';
import { Search, RotateCcw } from 'lucide-react';

interface AgentControlsProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedStatus: string;
  onStatusChange: (s: string) => void;
  selectedType: string;
  onTypeChange: (t: string) => void;
  selectedEnvironment: string;
  onEnvironmentChange: (e: string) => void;
  selectedRisk: string;
  onRiskChange: (r: string) => void;
  onReset: () => void;
}

export function AgentControls({
  searchQuery,
  onSearchChange,
  selectedStatus,
  onStatusChange,
  selectedType,
  onTypeChange,
  selectedEnvironment,
  onEnvironmentChange,
  selectedRisk,
  onRiskChange,
  onReset,
}: AgentControlsProps) {
  return (
    <div className="p-4 rounded-2xl border border-white/[0.08] bg-slate-900/60 backdrop-blur-xl space-y-3 font-mono text-xs shadow-2xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* SEARCH INPUT */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search agent ID, agent name, owner, policy..."
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500/50"
          />
        </div>

        {/* STATUS FILTER */}
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-slate-400 uppercase font-bold">STATUS:</span>
          <select
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
          >
            <option value="ALL">ALL STATUSES</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="IDLE">IDLE</option>
            <option value="SUSPENDED">SUSPENDED</option>
            <option value="DEGRADED">DEGRADED</option>
          </select>
        </div>

        {/* AGENT TYPE FILTER */}
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-slate-400 uppercase font-bold">TYPE:</span>
          <select
            value={selectedType}
            onChange={(e) => onTypeChange(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
          >
            <option value="ALL">ALL TYPES</option>
            <option value="AUTONOMOUS">AUTONOMOUS</option>
            <option value="SUPERVISED">SUPERVISED</option>
            <option value="WORKFLOW">WORKFLOW</option>
            <option value="SERVICE">SERVICE</option>
          </select>
        </div>

        {/* ENVIRONMENT FILTER */}
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-slate-400 uppercase font-bold">ENV:</span>
          <select
            value={selectedEnvironment}
            onChange={(e) => onEnvironmentChange(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
          >
            <option value="ALL">ALL ENVS</option>
            <option value="PRODUCTION">PRODUCTION</option>
            <option value="STAGING">STAGING</option>
            <option value="SANDBOX">SANDBOX</option>
          </select>
        </div>

        {/* RISK FILTER */}
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-slate-400 uppercase font-bold">RISK:</span>
          <select
            value={selectedRisk}
            onChange={(e) => onRiskChange(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
          >
            <option value="ALL">ALL RISKS</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
        </div>

        {/* RESET BUTTON */}
        <AGButton variant="ghost" size="sm" icon={RotateCcw} onClick={onReset}>
          RESET
        </AGButton>
      </div>
    </div>
  );
}
