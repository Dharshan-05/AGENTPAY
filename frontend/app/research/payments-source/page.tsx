'use client';

import { useState, useMemo } from 'react';
import './payments-source.css';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGCard, AGMetricCard, AGGlassCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { AGDrawer } from '@/components/ui/ag-drawer';
import {
  CreditCard,
  Search,
  Filter,
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
  RefreshCw,
  ArrowUpRight,
  Send,
  ExternalLink,
  Shield,
  Download,
  Calendar,
  DollarSign,
  ChevronRight,
  X,
  FileText,
  AlertTriangle,
  Lock,
  Layers,
  Sparkles,
  Zap,
  ArrowRight,
  Radio,
  Share2,
  Brain,
  Building2,
  Wallet,
  Receipt,
  Webhook,
} from 'lucide-react';

interface PaymentItem {
  id: string;
  amount: string;
  rawAmount: number;
  fee: string;
  net: string;
  status: 'AUTHORIZED' | 'CAPTURED' | 'SETTLED' | 'PROCESSING' | 'PENDING' | 'DECLINED' | 'FAILED' | 'REFUNDED';
  method: string;
  customerName: string;
  customerEmail: string;
  merchant: string;
  description: string;
  timestamp: string;
  ipAddress: string;
  agentGuardPolicy: string;
  fraudGuardScore: number;
  metadata: Record<string, string>;
}

const MOCK_PAYMENTS: PaymentItem[] = [
  {
    id: 'pay_9981A7b',
    amount: '$2,480.00',
    rawAmount: 2480.0,
    fee: '$72.40',
    net: '$2,407.60',
    status: 'AUTHORIZED',
    method: 'VISA ••••4242',
    customerName: 'Acme Procurement Inc',
    customerEmail: 'billing@acme.com',
    merchant: 'Acme Hardware Corp',
    description: 'Hardware GPU Server Batch #892',
    timestamp: '02:14:22 UTC',
    ipAddress: '103.14.88.19 (Frankfurt)',
    agentGuardPolicy: 'AGP-SPEND-004 (Passed)',
    fraudGuardScore: 18,
    metadata: { order_id: 'ORD-8921', agent_id: 'AGT-892', dept: 'Infrastructure' },
  },
  {
    id: 'pay_4412B9c',
    amount: '$1,240.00',
    rawAmount: 1240.0,
    fee: '$36.20',
    net: '$1,203.80',
    status: 'CAPTURED',
    method: 'GCASH ••••8921',
    customerName: 'ElectroHub Global',
    customerEmail: 'pay@electrohub.com',
    merchant: 'ElectroHub Direct',
    description: 'Component Supply Order #441',
    timestamp: '02:10:18 UTC',
    ipAddress: '198.51.100.42 (US-East)',
    agentGuardPolicy: 'AGP-TXN-002 (Passed)',
    fraudGuardScore: 48,
    metadata: { order_id: 'ORD-4412', agent_id: 'AGT-441', channel: 'Direct' },
  },
  {
    id: 'pay_2039C1d',
    amount: '$14,800.00',
    rawAmount: 14800.0,
    fee: '$0.00',
    net: '$0.00',
    status: 'FAILED',
    method: 'WIRE TRANSFER',
    customerName: 'Unverified Overseas Vendor',
    customerEmail: 'transfer@wire-gateway.io',
    merchant: 'Unknown Gateway',
    description: 'International Wire Deposit',
    timestamp: '01:58:44 UTC',
    ipAddress: '45.142.214.8 (Panama Proxy)',
    agentGuardPolicy: 'AGP-MER-003 (Blocked)',
    fraudGuardScore: 96,
    metadata: { order_id: 'ORD-2039', agent_id: 'AGT-203', flag: 'Sanctions Shield' },
  },
  {
    id: 'pay_1184D3e',
    amount: '$1,820.00',
    rawAmount: 1820.0,
    fee: '$52.80',
    net: '$1,767.20',
    status: 'SETTLED',
    method: 'MASTERCARD ••••8812',
    customerName: 'United Corp Travel',
    customerEmail: 'travel@unitedcorp.com',
    merchant: 'United Airlines',
    description: 'Corporate Flight Booking #118',
    timestamp: '01:45:10 UTC',
    ipAddress: '12.180.44.12 (Austin)',
    agentGuardPolicy: 'AGP-GOV-001 (Passed)',
    fraudGuardScore: 12,
    metadata: { order_id: 'ORD-1184', agent_id: 'AGT-118', category: 'Travel' },
  },
  {
    id: 'pay_7721E4f',
    amount: '$3,450.00',
    rawAmount: 3450.0,
    fee: '$0.00',
    net: '$0.00',
    status: 'REFUNDED',
    method: 'MAYA ••••1124',
    customerName: 'Logistics Supply Co',
    customerEmail: 'finance@logistics-co.com',
    merchant: 'Freight Logistics',
    description: 'Duplicate Freight Charge Reversal',
    timestamp: '01:20:05 UTC',
    ipAddress: '203.0.113.88 (Singapore)',
    agentGuardPolicy: 'AGP-REF-001 (Executed)',
    fraudGuardScore: 5,
    metadata: { order_id: 'ORD-7721', refund_reason: 'Duplicate Charge' },
  },
  {
    id: 'pay_5541F5g',
    amount: '$950.00',
    rawAmount: 950.0,
    fee: '$27.55',
    net: '$922.45',
    status: 'PROCESSING',
    method: 'VISA ••••1092',
    customerName: 'Design Studio LLC',
    customerEmail: 'hello@designstudio.io',
    merchant: 'Creative Assets',
    description: 'Enterprise Design Asset License',
    timestamp: '01:05:00 UTC',
    ipAddress: '198.51.100.99 (US-West)',
    agentGuardPolicy: 'AGP-SUB-009 (Pending)',
    fraudGuardScore: 22,
    metadata: { order_id: 'ORD-5541', plan: 'Enterprise' },
  },
];

export default function PaymentsSourceSynchronizedPage() {
  const [payments, setPayments] = useState<PaymentItem[]>(MOCK_PAYMENTS);
  const [selectedPaymentId, setSelectedPaymentId] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'1H' | '24H' | '7D'>('24H');

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [methodFilter, setMethodFilter] = useState<string>('ALL');

  // Selected Payment Object
  const selectedPayment = useMemo(
    () => payments.find((p) => p.id === selectedPaymentId) || null,
    [payments, selectedPaymentId]
  );

  // Filtered Payments
  const filteredPayments = useMemo(() => {
    return payments.filter((p) => {
      if (statusFilter !== 'ALL' && p.status !== statusFilter) return false;
      if (methodFilter !== 'ALL' && !p.method.toLowerCase().includes(methodFilter.toLowerCase())) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        return (
          p.id.toLowerCase().includes(q) ||
          p.customerName.toLowerCase().includes(q) ||
          p.merchant.toLowerCase().includes(q) ||
          p.description.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [payments, statusFilter, methodFilter, searchQuery]);

  // Handle Refund Action
  const handleRefund = (id: string) => {
    setPayments((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: 'REFUNDED' as const } : item))
    );
  };

  return (
    <AgentPayShell activeTab="payments">
      <div className="space-y-6 pb-12 payments-source-dark-root">
        
        {/* MASTER PAGE HEADER */}
        <PageHeader
          eyebrow="AUTONOMOUS PAYMENT EXECUTION & TRANSACTION INTELLIGENCE"
          title="PAY"
          highlightTitle="MENTS"
          description="Autonomous payment execution, transaction intelligence, settlement monitoring, and payment lifecycle control."
          icon={CreditCard}
          statusBadge={
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              PAYMENT ENGINE ONLINE (v2.4)
            </span>
          }
          actions={
            <>
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-white/[0.06] font-mono text-xs text-slate-300">
                <span>MODEL:</span>
                <span className="text-blue-400 font-bold">PAY-ENGINE-XGB</span>
              </div>
              <AGButton variant="ghost" size="md" icon={RefreshCw}>
                Refresh Feed
              </AGButton>
              <AGButton variant="primary" size="md" icon={Download}>
                Export Audit Logs
              </AGButton>
            </>
          }
        />

        {/* 4 MASTER AGENTPAY TELEMETRY KPI CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard
            label="24H PAYMENT VOLUME"
            value="$142,850.00"
            subtext="+14.2% VS YESTERDAY"
            trend="+14.2%"
            trendPositive={true}
            accentColor="text-emerald-400"
          />

          <AGMetricCard
            label="SUCCESSFUL PAYMENTS"
            value="1,284"
            subtext="94.2% SUCCESS RATE"
            trend="1,284 Clear"
            trendPositive={true}
            accentColor="text-emerald-400"
          />

          <AGMetricCard
            label="FAILED / DECLINED"
            value="42"
            subtext="3.1% FAILURE RATE"
            trend="42 Blocked"
            trendPositive={false}
            accentColor="text-red-400"
          />

          <AGMetricCard
            label="NET SETTLEMENT"
            value="$138,564.50"
            subtext="AFTER FEES"
            trend="T+1 Schedule"
            trendPositive={true}
            accentColor="text-blue-400"
          />
        </div>

        {/* PAYMENT INTELLIGENCE & TELEMETRY SECTION */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* LEFT 2 COLS: PAYMENT OPERATIONS TELEMETRY CHART */}
          <div className="lg:col-span-2 space-y-4">
            <AGCard className="space-y-4">
              <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] font-mono text-xs gap-3">
                <div className="flex items-center gap-2 font-bold text-slate-100">
                  <Activity className="w-4 h-4 text-emerald-400" />
                  <span>PAYMENT OPERATIONS TELEMETRY</span>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-white/10 text-[10px]">
                    {(['1H', '24H', '7D'] as const).map((r) => (
                      <button
                        key={r}
                        onClick={() => setTimeRange(r)}
                        className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                          timeRange === r
                            ? 'bg-emerald-500 text-slate-950 shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                            : 'text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        {r}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Chart SVG Visualization */}
              <div className="h-60 rounded-xl bg-slate-950/90 border border-white/[0.04] p-4 flex flex-col justify-between font-mono text-xs relative overflow-hidden">
                <div className="flex justify-between items-center text-[10px] text-slate-500">
                  <span>Settlement Volume vs Transaction Authorization Activity</span>
                  <span>Live Telemetry Stream</span>
                </div>

                <div className="h-40 w-full flex items-end justify-between gap-3 pt-4">
                  {[
                    { vol: 35, auth: 28, pend: 10, fail: 5 },
                    { vol: 48, auth: 40, pend: 12, fail: 4 },
                    { vol: 62, auth: 55, pend: 15, fail: 6 },
                    { vol: 80, auth: 72, pend: 18, fail: 8 },
                    { vol: 94, auth: 88, pend: 20, fail: 12 },
                    { vol: 70, auth: 62, pend: 14, fail: 5 },
                    { vol: 55, auth: 48, pend: 10, fail: 3 },
                    { vol: 88, auth: 82, pend: 22, fail: 9 },
                    { vol: 64, auth: 58, pend: 16, fail: 4 },
                    { vol: 76, auth: 70, pend: 14, fail: 6 },
                  ].map((d, idx) => (
                    <div key={idx} className="flex-1 flex items-end justify-center gap-1 h-full">
                      <div
                        className="w-1/4 bg-emerald-500/80 rounded-t hover:bg-emerald-400 transition-colors"
                        style={{ height: `${d.vol}%` }}
                        title={`Volume: ${d.vol}%`}
                      />
                      <div
                        className="w-1/4 bg-blue-500/80 rounded-t hover:bg-blue-400 transition-colors"
                        style={{ height: `${d.auth}%` }}
                        title={`Authorized: ${d.auth}%`}
                      />
                      <div
                        className="w-1/4 bg-amber-500/80 rounded-t hover:bg-amber-400 transition-colors"
                        style={{ height: `${d.pend}%` }}
                        title={`Pending: ${d.pend}%`}
                      />
                      <div
                        className="w-1/4 bg-red-500/80 rounded-t hover:bg-red-400 transition-colors"
                        style={{ height: `${d.fail}%` }}
                        title={`Failed: ${d.fail}%`}
                      />
                    </div>
                  ))}
                </div>

                {/* Legend Footer */}
                <div className="flex items-center justify-between text-[10px] pt-2 border-t border-white/[0.06] text-slate-400">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded bg-emerald-400" /> Payment Volume</span>
                    <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded bg-blue-400" /> Authorized</span>
                    <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded bg-amber-400" /> Pending</span>
                    <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded bg-red-400" /> Failed</span>
                  </div>
                  <span>Peak Processing Capacity: 98.4%</span>
                </div>
              </div>
            </AGCard>
          </div>

          {/* RIGHT 1 COL: SETTLEMENT OPERATIONS PANEL */}
          <div className="space-y-4">
            <AGCard className="space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] font-mono text-xs">
                <span className="font-bold text-slate-100 flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-blue-400" /> SETTLEMENT OPERATIONS
                </span>
                <AGBadge status="POLICY_SECURE" label="T+1 ACTIVE" />
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Today's Settlement Payout</span>
                  <div className="text-xl font-bold text-emerald-400">$138,564.50</div>
                  <span className="text-[10px] text-slate-500">Batch #po_8812A · Cleared</span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
                    <span className="text-[10px] text-slate-400 block">Pending Clearance</span>
                    <span className="font-bold text-amber-400">$24,820.00</span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
                    <span className="text-[10px] text-slate-400 block">Processing Fees</span>
                    <span className="font-bold text-slate-300">$4,285.50</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-1.5 text-[11px]">
                  <div className="flex justify-between items-center text-blue-400 font-bold">
                    <span>Destination Bank Account</span>
                    <span>Chase Bank (••••4491)</span>
                  </div>
                  <p className="text-[10px] text-slate-300 leading-relaxed">
                    Automated daily settlement wire scheduled for 23:00 UTC. Next payout: $24,820.00.
                  </p>
                </div>
              </div>
            </AGCard>
          </div>

        </div>

        {/* LIVE TRANSACTION OPERATIONS & FILTER BAR */}
        <AGCard className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-white/[0.08] font-mono text-xs">
            <div className="flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-emerald-400" />
              <span className="font-bold text-slate-100 text-sm">LIVE TRANSACTION OPERATIONS</span>
              <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px]">
                {filteredPayments.length} Transactions
              </span>
            </div>

            {/* Dark Filter Bar Controls */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search payment ID, customer, merchant..."
                  className="pl-9 pr-3 py-1.5 bg-slate-950 border border-white/10 rounded-xl text-[11px] text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500/50"
                />
              </div>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-slate-950 border border-white/10 rounded-xl px-3 py-1.5 text-[11px] text-slate-300 focus:outline-none"
              >
                <option value="ALL">Status: All</option>
                <option value="AUTHORIZED">AUTHORIZED</option>
                <option value="CAPTURED">CAPTURED</option>
                <option value="SETTLED">SETTLED</option>
                <option value="PROCESSING">PROCESSING</option>
                <option value="FAILED">FAILED</option>
                <option value="REFUNDED">REFUNDED</option>
              </select>

              <select
                value={methodFilter}
                onChange={(e) => setMethodFilter(e.target.value)}
                className="bg-slate-950 border border-white/10 rounded-xl px-3 py-1.5 text-[11px] text-slate-300 focus:outline-none"
              >
                <option value="ALL">Method: All</option>
                <option value="VISA">Visa</option>
                <option value="MASTERCARD">Mastercard</option>
                <option value="GCASH">GCash</option>
                <option value="MAYA">Maya</option>
                <option value="WIRE">Wire Transfer</option>
              </select>

              <AGButton
                variant="ghost"
                size="sm"
                icon={Filter}
                onClick={() => {
                  setSearchQuery('');
                  setStatusFilter('ALL');
                  setMethodFilter('ALL');
                }}
              >
                Reset
              </AGButton>
            </div>
          </div>

          {/* Table Element */}
          <div className="overflow-x-auto font-mono text-xs">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] bg-slate-950/60 text-slate-400 text-[10px] uppercase tracking-wider">
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Payment ID</th>
                  <th className="p-3.5">Amount</th>
                  <th className="p-3.5">Method</th>
                  <th className="p-3.5">Customer</th>
                  <th className="p-3.5">Merchant / Description</th>
                  <th className="p-3.5">Created</th>
                  <th className="p-3.5">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filteredPayments.map((p) => {
                  const isSelected = selectedPaymentId === p.id;
                  return (
                    <tr
                      key={p.id}
                      onClick={() => setSelectedPaymentId(p.id)}
                      className={`cursor-pointer transition-colors ${
                        isSelected ? 'bg-emerald-500/10 border-l-2 border-l-emerald-400' : 'hover:bg-slate-800/40'
                      }`}
                    >
                      <td className="p-3.5">
                        <AGBadge
                          status={
                            p.status === 'AUTHORIZED' || p.status === 'CAPTURED' || p.status === 'SETTLED'
                              ? 'APPROVED'
                              : p.status === 'PROCESSING' || p.status === 'PENDING'
                              ? 'PENDING'
                              : p.status === 'FAILED'
                              ? 'BLOCKED'
                              : 'REVIEW'
                          }
                          label={`● ${p.status}`}
                        />
                      </td>

                      <td className="p-3.5 font-bold text-slate-100">{p.id}</td>
                      <td className="p-3.5 text-emerald-400 font-bold">{p.amount}</td>
                      <td className="p-3.5 text-slate-300 font-semibold">{p.method}</td>
                      <td className="p-3.5 text-slate-300">
                        {p.customerName} <div className="text-[10px] text-slate-500">{p.customerEmail}</div>
                      </td>
                      <td className="p-3.5 text-slate-300 max-w-xs truncate">{p.description}</td>
                      <td className="p-3.5 text-slate-400 text-[10px]">{p.timestamp}</td>

                      <td className="p-3.5">
                        <AGButton variant="ghost" size="sm">
                          Inspect
                        </AGButton>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </AGCard>

        {/* WEBHOOK & EVENT STREAM TELEMETRY */}
        <AGCard className="space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
            <span className="font-bold text-slate-100 flex items-center gap-2">
              <Webhook className="w-4 h-4 text-blue-400" /> WEBHOOK & EVENT TELEMETRY STREAM
            </span>
            <span className="text-[10px] text-slate-500">Live Socket Feed</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.04] space-y-2 text-[11px]">
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-emerald-400 font-bold">14:28:22 UTC</span>
              <span className="text-blue-400 font-bold">PAYMENT.AUTHORIZED</span>
              <span className="text-slate-400">pay_9981A7b</span>
              <span className="text-emerald-400">200 OK (14ms)</span>
            </div>
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-emerald-400 font-bold">14:28:24 UTC</span>
              <span className="text-blue-400 font-bold">PAYMENT.CAPTURED</span>
              <span className="text-slate-400">pay_9981A7b</span>
              <span className="text-emerald-400">200 OK (18ms)</span>
            </div>
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-emerald-400 font-bold">14:28:27 UTC</span>
              <span className="text-purple-400 font-bold">SETTLEMENT.CREATED</span>
              <span className="text-slate-400">po_8812A</span>
              <span className="text-emerald-400">200 OK (12ms)</span>
            </div>
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-emerald-400 font-bold">14:28:29 UTC</span>
              <span className="text-amber-400 font-bold">WEBHOOK.DELIVERED</span>
              <span className="text-slate-400">evt_91AB42</span>
              <span className="text-emerald-400">200 OK (15ms)</span>
            </div>
          </div>
        </AGCard>

        {/* PAYMENT INSPECTOR AGDRAWER (SLIDE-OVER DRAWER) */}
        <AGDrawer
          isOpen={!!selectedPayment}
          onClose={() => setSelectedPaymentId(null)}
          title={selectedPayment ? `PAYMENT INSPECTOR: ${selectedPayment.id}` : 'PAYMENT INSPECTOR'}
          subtitle="AUTONOMOUS PAYMENT EXECUTION & LIFECYCLE AUDIT"
          footer={
            selectedPayment && (
              <div className="space-y-3 font-mono">
                <div className="grid grid-cols-2 gap-2">
                  <AGButton
                    variant="danger"
                    size="md"
                    onClick={() => handleRefund(selectedPayment.id)}
                    disabled={selectedPayment.status === 'REFUNDED'}
                  >
                    {selectedPayment.status === 'REFUNDED' ? 'REFUNDED' : 'ISSUE REFUND'}
                  </AGButton>

                  <AGButton
                    variant="primary"
                    size="md"
                    onClick={() => setSelectedPaymentId(null)}
                  >
                    CLOSE INSPECTOR
                  </AGButton>
                </div>

                <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-white/[0.08]">
                  <span>Policy Check: {selectedPayment.agentGuardPolicy}</span>
                  <span>Risk Score: {selectedPayment.fraudGuardScore}/100</span>
                </div>
              </div>
            )
          }
        >
          {selectedPayment && (
            <div className="space-y-6 font-mono text-xs">
              
              {/* STATUS BANNER */}
              <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-400 block">TRANSACTION VERDICT</span>
                  <span className="text-base font-bold text-slate-100">{selectedPayment.status}</span>
                </div>

                <AGBadge
                  status={
                    selectedPayment.status === 'AUTHORIZED' || selectedPayment.status === 'CAPTURED' || selectedPayment.status === 'SETTLED'
                      ? 'APPROVED'
                      : selectedPayment.status === 'FAILED'
                      ? 'BLOCKED'
                      : 'PENDING'
                  }
                  label={`NET: ${selectedPayment.net}`}
                />
              </div>

              {/* FINANCIAL SUMMARY */}
              <div className="space-y-2">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                  FINANCIAL SUMMARY & BREAKDOWN
                </h4>
                <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.06] space-y-2 text-[11px]">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Gross Payment Amount:</span>
                    <span className="text-slate-100 font-bold">{selectedPayment.amount}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Processing Fee:</span>
                    <span className="text-slate-400">{selectedPayment.fee}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Net Merchant Payout:</span>
                    <span className="text-emerald-400 font-bold">{selectedPayment.net}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Payment Instrument:</span>
                    <span className="text-slate-200">{selectedPayment.method}</span>
                  </div>
                </div>
              </div>

              {/* CUSTOMER & AGENT CONTEXT */}
              <div className="space-y-2">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                  CUSTOMER & AGENT IDENTITY
                </h4>
                <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1.5 text-[11px]">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Customer Name:</span>
                    <span className="text-slate-200 font-bold">{selectedPayment.customerName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Customer Email:</span>
                    <span className="text-slate-300">{selectedPayment.customerEmail}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Merchant Target:</span>
                    <span className="text-slate-200">{selectedPayment.merchant}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">IP Node:</span>
                    <span className="text-slate-400 text-[10px]">{selectedPayment.ipAddress}</span>
                  </div>
                </div>
              </div>

              {/* CONNECTED LIFECYCLE TIMELINE */}
              <div className="space-y-2">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-emerald-400" />
                  CONNECTED PAYMENT LIFECYCLE TIMELINE
                </h4>
                <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.06] space-y-3 text-[10px]">
                  <div className="flex items-center justify-between text-slate-300">
                    <span className="text-emerald-400 font-bold">01 PAYMENT CREATED</span>
                    <span className="text-slate-500">{selectedPayment.timestamp}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-300">
                    <span className="text-blue-400 font-bold">02 AGENTGUARD POLICY CHECK</span>
                    <span className="text-slate-400">{selectedPayment.agentGuardPolicy}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-300">
                    <span className="text-purple-400 font-bold">03 FRAUDGUARD RISK EVALUATION</span>
                    <span className="text-slate-400">Score: {selectedPayment.fraudGuardScore}/100</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-300">
                    <span className="text-emerald-400 font-bold">04 AUTHORIZATION & CAPTURE</span>
                    <span className="text-emerald-400 font-bold">{selectedPayment.status}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-300">
                    <span className="text-blue-400 font-bold">05 SETTLEMENT PAYOUT</span>
                    <span className="text-slate-400">Scheduled T+1</span>
                  </div>
                </div>
              </div>

              {/* METADATA PAYLOAD */}
              <div className="space-y-2">
                <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                  METADATA PAYLOAD (JSON)
                </h4>
                <pre className="p-3 rounded-xl bg-slate-950 border border-white/[0.04] text-[10px] text-emerald-400 overflow-x-auto">
                  {JSON.stringify(selectedPayment.metadata, null, 2)}
                </pre>
              </div>

            </div>
          )}
        </AGDrawer>

      </div>
    </AgentPayShell>
  );
}
