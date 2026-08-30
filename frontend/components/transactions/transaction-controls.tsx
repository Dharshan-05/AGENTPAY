'use client';

interface TransactionControlsProps {
  searchQuery: string;
  onSearchChange: (v: string) => void;
  selectedStatus: string;
  onStatusChange: (v: string) => void;
  selectedProcessor: string;
  onProcessorChange: (v: string) => void;
  selectedMethod: string;
  onMethodChange: (v: string) => void;
  selectedRisk: string;
  onRiskChange: (v: string) => void;
  selectedAgent: string;
  onAgentChange: (v: string) => void;
  selectedEnvironment: string;
  onEnvironmentChange: (v: string) => void;
  selectedDate: string;
  onDateChange: (v: string) => void;
  onReset: () => void;
}

export function TransactionControls({
  searchQuery,
  onSearchChange,
  selectedStatus,
  onStatusChange,
  selectedProcessor,
  onProcessorChange,
  selectedMethod,
  onMethodChange,
  selectedRisk,
  onRiskChange,
  selectedAgent,
  onAgentChange,
  selectedEnvironment,
  onEnvironmentChange,
  selectedDate,
  onDateChange,
  onReset,
}: TransactionControlsProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl">
      <div className="flex flex-wrap gap-3 items-end">
        {/* SEARCH */}
        <div className="flex-1 min-w-[220px]">
          <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block mb-1">
            SEARCH TRANSACTIONS
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search TXN-ID, Agent, PI-ID, Merchant..."
            className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:border-blue-500/40 focus:outline-none transition-colors"
          />
        </div>

        {/* STATUS */}
        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">STATUS</label>
          <select
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL STATUSES</option>
            <option value="PENDING">PENDING</option>
            <option value="AUTHORIZED">AUTHORIZED</option>
            <option value="CAPTURED">CAPTURED</option>
            <option value="SETTLED">SETTLED</option>
            <option value="FAILED">FAILED</option>
            <option value="DECLINED">DECLINED</option>
            <option value="REFUNDED">REFUNDED</option>
            <option value="DISPUTED">DISPUTED</option>
            <option value="BLOCKED">BLOCKED</option>
            <option value="UNDER_REVIEW">UNDER REVIEW</option>
          </select>
        </div>

        {/* PROCESSOR */}
        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">PROCESSOR</label>
          <select
            value={selectedProcessor}
            onChange={(e) => onProcessorChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL PROCESSORS</option>
            <option value="Stripe">Stripe</option>
            <option value="Adyen">Adyen</option>
            <option value="Visa Direct">Visa Direct</option>
            <option value="JPMorgan">JPMorgan</option>
            <option value="Citibank">Citibank</option>
          </select>
        </div>

        {/* METHOD */}
        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">METHOD</label>
          <select
            value={selectedMethod}
            onChange={(e) => onMethodChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL METHODS</option>
            <option value="VIRTUAL_CARD">VIRTUAL CARD</option>
            <option value="CARD">CARD</option>
            <option value="BANK_TRANSFER">BANK TRANSFER</option>
            <option value="ACH">ACH</option>
            <option value="UPI">UPI</option>
            <option value="WALLET">WALLET</option>
          </select>
        </div>

        {/* RISK */}
        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">RISK</label>
          <select
            value={selectedRisk}
            onChange={(e) => onRiskChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL RISK TIERS</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
        </div>

        {/* AGENT */}
        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">AGENT</label>
          <select
            value={selectedAgent}
            onChange={(e) => onAgentChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL AGENTS</option>
            <option value="AGT-892">AGT-892 (Procurement)</option>
            <option value="AGT-441">AGT-441 (Vendor Payout)</option>
            <option value="AGT-118">AGT-118 (Invoice Recon)</option>
          </select>
        </div>

        {/* ENVIRONMENT */}
        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">ENV</label>
          <select
            value={selectedEnvironment}
            onChange={(e) => onEnvironmentChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL ENV</option>
            <option value="PRODUCTION">PRODUCTION</option>
            <option value="STAGING">STAGING</option>
            <option value="SANDBOX">SANDBOX</option>
          </select>
        </div>

        {/* DATE */}
        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">TIMEFRAME</label>
          <select
            value={selectedDate}
            onChange={(e) => onDateChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL TIME</option>
            <option value="24H">LAST 24 HOURS</option>
            <option value="7D">LAST 7 DAYS</option>
            <option value="30D">LAST 30 DAYS</option>
          </select>
        </div>

        {/* RESET */}
        <button
          onClick={onReset}
          className="px-4 py-2 rounded-xl border border-white/[0.08] text-xs font-mono text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 transition-all"
        >
          RESET
        </button>
      </div>
    </div>
  );
}
