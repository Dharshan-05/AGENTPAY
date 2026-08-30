'use client';

interface PaymentMethodControlsProps {
  searchQuery: string;
  onSearchChange: (v: string) => void;
  selectedType: string;
  onTypeChange: (v: string) => void;
  selectedStatus: string;
  onStatusChange: (v: string) => void;
  selectedProcessor: string;
  onProcessorChange: (v: string) => void;
  selectedAgent: string;
  onAgentChange: (v: string) => void;
  selectedRiskTier: string;
  onRiskTierChange: (v: string) => void;
  selectedEnvironment: string;
  onEnvironmentChange: (v: string) => void;
  selectedCountry: string;
  onCountryChange: (v: string) => void;
  selectedCurrency: string;
  onCurrencyChange: (v: string) => void;
  onReset: () => void;
}

export function PaymentMethodControls({
  searchQuery,
  onSearchChange,
  selectedType,
  onTypeChange,
  selectedStatus,
  onStatusChange,
  selectedProcessor,
  onProcessorChange,
  selectedAgent,
  onAgentChange,
  selectedRiskTier,
  onRiskTierChange,
  selectedEnvironment,
  onEnvironmentChange,
  selectedCountry,
  onCountryChange,
  selectedCurrency,
  onCurrencyChange,
  onReset,
}: PaymentMethodControlsProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs">
      <div className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[200px]">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">
            SEARCH PAYMENT METHODS &amp; INSTRUMENTS
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search PM ID, Card, Bank, VPA, Agent, Owner, Token..."
            className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:border-blue-500/40 focus:outline-none"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider">TYPE</label>
          <select
            value={selectedType}
            onChange={(e) => onTypeChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL TYPES</option>
            <option value="CARD">CARD</option>
            <option value="VIRTUAL_CARD">VIRTUAL_CARD</option>
            <option value="BANK_ACCOUNT">BANK_ACCOUNT</option>
            <option value="UPI">UPI</option>
            <option value="WALLET">WALLET</option>
            <option value="BANK_TRANSFER">BANK_TRANSFER</option>
            <option value="BNPL">BNPL</option>
            <option value="TOKENIZED_CARD">TOKENIZED_CARD</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider">STATUS</label>
          <select
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL STATUSES</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="VERIFIED">VERIFIED</option>
            <option value="DEGRADED">DEGRADED</option>
            <option value="RESTRICTED">RESTRICTED</option>
            <option value="SUSPENDED">SUSPENDED</option>
            <option value="EXPIRING_SOON">EXPIRING_SOON</option>
            <option value="EXPIRED">EXPIRED</option>
            <option value="REVOKED">REVOKED</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider">PROCESSOR</label>
          <select
            value={selectedProcessor}
            onChange={(e) => onProcessorChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL PROCESSORS</option>
            <option value="Stripe">Stripe</option>
            <option value="Adyen">Adyen</option>
            <option value="JPMorgan Direct">JPMorgan Direct</option>
            <option value="Citibank Direct">Citibank Direct</option>
            <option value="Razorpay">Razorpay</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider">AGENT</label>
          <select
            value={selectedAgent}
            onChange={(e) => onAgentChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL AGENTS</option>
            <option value="AGT-892">AGT-892 (Procurement)</option>
            <option value="AGT-441">AGT-441 (Vendor Payment)</option>
            <option value="AGT-118">AGT-118 (Reconciliation)</option>
            <option value="AGT-990">AGT-990 (Trading)</option>
            <option value="AGT-301">AGT-301 (Logistics)</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider">RISK TIER</label>
          <select
            value={selectedRiskTier}
            onChange={(e) => onRiskTierChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL RISK TIERS</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider">ENV</label>
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
