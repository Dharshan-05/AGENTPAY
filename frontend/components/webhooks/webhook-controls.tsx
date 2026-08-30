'use client';

interface WebhookControlsProps {
  searchQuery: string;
  onSearchChange: (v: string) => void;
  selectedStatus: string;
  onStatusChange: (v: string) => void;
  selectedEventType: string;
  onEventTypeChange: (v: string) => void;
  selectedEndpoint: string;
  onEndpointChange: (v: string) => void;
  selectedEnvironment: string;
  onEnvironmentChange: (v: string) => void;
  selectedHttpStatus: string;
  onHttpStatusChange: (v: string) => void;
  onReset: () => void;
}

export function WebhookControls({
  searchQuery,
  onSearchChange,
  selectedStatus,
  onStatusChange,
  selectedEventType,
  onEventTypeChange,
  selectedEndpoint,
  onEndpointChange,
  selectedEnvironment,
  onEnvironmentChange,
  selectedHttpStatus,
  onHttpStatusChange,
  onReset,
}: WebhookControlsProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs">
      <div className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[200px]">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">
            SEARCH WEBHOOK OPERATIONS
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search Endpoint, EVT-ID, Delivery ID, Agent, Transaction..."
            className="w-full bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:border-blue-500/40 focus:outline-none"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider">STATUS</label>
          <select
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL STATUSES</option>
            <option value="HEALTHY">HEALTHY</option>
            <option value="DEGRADED">DEGRADED</option>
            <option value="FAILING">FAILING</option>
            <option value="DELIVERED">DELIVERED</option>
            <option value="FAILED">FAILED</option>
            <option value="RETRYING">RETRYING</option>
            <option value="EXHAUSTED">EXHAUSTED</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider">EVENT TYPE</label>
          <select
            value={selectedEventType}
            onChange={(e) => onEventTypeChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL EVENT TYPES</option>
            <option value="transaction.captured">transaction.captured</option>
            <option value="policy.blocked">policy.blocked</option>
            <option value="risk.alerted">risk.alerted</option>
            <option value="refund.succeeded">refund.succeeded</option>
            <option value="agent.suspended">agent.suspended</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider">ENDPOINT</label>
          <select
            value={selectedEndpoint}
            onChange={(e) => onEndpointChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL ENDPOINTS</option>
            <option value="WHK-001">WHK-001 (Finance Gateway)</option>
            <option value="WHK-002">WHK-002 (Fraud Monitor)</option>
            <option value="WHK-003">WHK-003 (ERP Sync)</option>
            <option value="WHK-004">WHK-004 (Sandbox)</option>
            <option value="WHK-005">WHK-005 (Legacy)</option>
            <option value="WHK-006">WHK-006 (Staging)</option>
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

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-slate-500 uppercase tracking-wider">HTTP CODE</label>
          <select
            value={selectedHttpStatus}
            onChange={(e) => onHttpStatusChange(e.target.value)}
            className="bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:border-blue-500/40 focus:outline-none"
          >
            <option value="ALL">ALL HTTP CODES</option>
            <option value="200">200 OK</option>
            <option value="503">503 Service Unavailable</option>
            <option value="504">504 Gateway Timeout</option>
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
