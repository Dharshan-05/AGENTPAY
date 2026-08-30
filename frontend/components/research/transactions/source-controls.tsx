'use client';

import { Search, RotateCcw, SlidersHorizontal } from 'lucide-react';

interface SourceControlsProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedProcessor: string;
  onProcessorChange: (p: string) => void;
  selectedStatus: string;
  onStatusChange: (s: string) => void;
  selectedPaymentMethod: string;
  onPaymentMethodChange: (m: string) => void;
  selectedRiskTier: string;
  onRiskTierChange: (r: string) => void;
  selectedAgent: string;
  onAgentChange: (a: string) => void;
  selectedEnvironment: string;
  onEnvironmentChange: (e: string) => void;
  onReset: () => void;
}

export function SourceControls({
  searchQuery,
  onSearchChange,
  selectedProcessor,
  onProcessorChange,
  selectedStatus,
  onStatusChange,
  selectedPaymentMethod,
  onPaymentMethodChange,
  selectedRiskTier,
  onRiskTierChange,
  selectedAgent,
  onAgentChange,
  selectedEnvironment,
  onEnvironmentChange,
  onReset,
}: SourceControlsProps) {
  const selectClass = "px-2.5 py-1.5 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 font-semibold focus:outline-none focus:border-blue-400 cursor-pointer";

  return (
    <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm font-sans">
      <div className="flex items-center gap-2 mb-3">
        <SlidersHorizontal className="w-3.5 h-3.5 text-slate-400" />
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">TRANSACTION FILTERS</span>
      </div>
      <div className="flex flex-wrap items-center gap-2.5">
        {/* SEARCH */}
        <div className="relative flex-1 min-w-[260px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search Txn ID · Intent ID · Agent · Merchant · Amount..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-blue-400 font-sans"
          />
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-slate-400 uppercase font-bold">STATUS</span>
          <select value={selectedStatus} onChange={(e) => onStatusChange(e.target.value)} className={selectClass}>
            <option value="ALL">ALL</option>
            <option value="PENDING">PENDING</option>
            <option value="AUTHORIZED">AUTHORIZED</option>
            <option value="CAPTURED">CAPTURED</option>
            <option value="SETTLED">SETTLED</option>
            <option value="UNDER_REVIEW">UNDER REVIEW</option>
            <option value="REQUIRES_ACTION">REQUIRES ACTION</option>
            <option value="BLOCKED">BLOCKED</option>
            <option value="FAILED">FAILED</option>
            <option value="REFUNDED">REFUNDED</option>
            <option value="DISPUTED">DISPUTED</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-slate-400 uppercase font-bold">PROCESSOR</span>
          <select value={selectedProcessor} onChange={(e) => onProcessorChange(e.target.value)} className={selectClass}>
            <option value="ALL">ALL PROCESSORS</option>
            <option value="Stripe">STRIPE</option>
            <option value="Adyen">ADYEN</option>
            <option value="Visa Direct">VISA DIRECT</option>
            <option value="JPMorgan">JPMORGAN</option>
            <option value="Citibank">CITIBANK</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-slate-400 uppercase font-bold">METHOD</span>
          <select value={selectedPaymentMethod} onChange={(e) => onPaymentMethodChange(e.target.value)} className={selectClass}>
            <option value="ALL">ALL METHODS</option>
            <option value="VIRTUAL_CARD">VIRTUAL CARD</option>
            <option value="CARD">CARD</option>
            <option value="BANK_TRANSFER">BANK TRANSFER</option>
            <option value="ACH">ACH</option>
            <option value="UPI">UPI</option>
            <option value="WALLET">WALLET</option>
            <option value="NET_BANKING">NET BANKING</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-slate-400 uppercase font-bold">RISK</span>
          <select value={selectedRiskTier} onChange={(e) => onRiskTierChange(e.target.value)} className={selectClass}>
            <option value="ALL">ALL RISK TIERS</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-slate-400 uppercase font-bold">AGENT</span>
          <select value={selectedAgent} onChange={(e) => onAgentChange(e.target.value)} className={selectClass}>
            <option value="ALL">ALL AGENTS</option>
            <option value="AGT-892">AGT-892</option>
            <option value="AGT-441">AGT-441</option>
            <option value="AGT-118">AGT-118</option>
            <option value="AGT-290">AGT-290</option>
            <option value="AGT-570">AGT-570</option>
            <option value="AGT-891">AGT-891</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-slate-400 uppercase font-bold">ENV</span>
          <select value={selectedEnvironment} onChange={(e) => onEnvironmentChange(e.target.value)} className={selectClass}>
            <option value="ALL">ALL ENVIRONMENTS</option>
            <option value="PRODUCTION">PRODUCTION</option>
            <option value="STAGING">STAGING</option>
            <option value="SANDBOX">SANDBOX</option>
          </select>
        </div>

        <button
          onClick={onReset}
          className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 font-semibold rounded-xl border border-slate-200 flex items-center gap-1.5 transition-colors text-xs"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset
        </button>
      </div>
    </div>
  );
}
