'use client';

import { Search, Filter, RotateCcw } from 'lucide-react';

interface SourceControlsProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedStatus: string;
  onStatusChange: (s: string) => void;
  selectedType: string;
  onTypeChange: (t: string) => void;
  selectedEnvironment: string;
  onEnvironmentChange: (e: string) => void;
  onReset: () => void;
}

export function SourceControls({
  searchQuery,
  onSearchChange,
  selectedStatus,
  onStatusChange,
  selectedType,
  onTypeChange,
  selectedEnvironment,
  onEnvironmentChange,
  onReset,
}: SourceControlsProps) {
  return (
    <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3 font-sans text-xs">
      <div className="flex flex-wrap items-center justify-between gap-3 font-mono">
        {/* SEARCH INPUT */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search Agent ID, Agent Name, Owner, Policy..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-blue-500 font-sans"
          />
        </div>

        {/* STATUS FILTER */}
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-slate-400 uppercase font-bold">STATUS:</span>
          <select
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 font-bold focus:outline-none"
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
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 font-bold focus:outline-none"
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
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 font-bold focus:outline-none"
          >
            <option value="ALL">ALL ENVS</option>
            <option value="PRODUCTION">PRODUCTION</option>
            <option value="STAGING">STAGING</option>
            <option value="SANDBOX">SANDBOX</option>
          </select>
        </div>

        {/* RESET BUTTON */}
        <button
          onClick={onReset}
          className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl border border-slate-200 flex items-center gap-1 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" /> Reset
        </button>
      </div>
    </div>
  );
}
