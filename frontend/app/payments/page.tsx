'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PaymentHeader } from '@/components/payments/payment-header';
import { PaymentMetrics } from '@/components/payments/payment-metrics';
import { PaymentTabs, PaymentTabType } from '@/components/payments/payment-tabs';
import { PaymentFilters } from '@/components/payments/payment-filters';
import { PaymentTable } from '@/components/payments/payment-table';
import { PaymentInspector } from '@/components/payments/payment-inspector';
import { WebhookEvents } from '@/components/payments/webhook-events';
import { CheckoutTester } from '@/components/payments/checkout-tester';
import { Settlements } from '@/components/payments/settlements';
import { PaymentRecord, WebhookEventRecord, SettlementRecord } from '@/components/payments/types';

const INITIAL_PAYMENTS: PaymentRecord[] = [
  {
    id: 'pay_9981A7b',
    amount: '$2,480.00',
    rawAmount: 2480.0,
    fee: '$72.40',
    net: '$2,407.60',
    status: 'AUTHORIZED',
    method: 'Visa ****4242',
    methodType: 'VISA',
    customerName: 'Acme Procurement Inc',
    customerEmail: 'billing@acme.com',
    merchant: 'Acme Hardware Corp',
    description: 'Hardware GPU Server Batch #892',
    agentName: 'Procurement Agent #892',
    agentId: 'AGT-892',
    policy: 'AGP-GOV-001',
    riskScore: 8,
    riskBand: 'LOW',
    agentGuardStatus: 'POLICY SECURE',
    fraudGuardStatus: 'CLEAN',
    txnHash: '0x9F4AC8102E3B881900281F7A9B8411',
    timestamp: '02:14:22 UTC',
    ipAddress: '103.14.88.19 (Frankfurt)',
    metadata: { order_id: 'ORD-8921', dept: 'Infrastructure', agent: 'AGT-892' },
  },
  {
    id: 'pay_4412B9c',
    amount: '$1,240.00',
    rawAmount: 1240.0,
    fee: '$36.20',
    net: '$1,203.80',
    status: 'CAPTURED',
    method: 'GCash 0917****892',
    methodType: 'GCASH',
    customerName: 'ElectroHub Global',
    customerEmail: 'pay@electrohub.com',
    merchant: 'ElectroHub Direct',
    description: 'Component Supply Order #441',
    agentName: 'Shopping Agent #441',
    agentId: 'AGT-441',
    policy: 'AGP-TXN-002',
    riskScore: 48,
    riskBand: 'MEDIUM',
    agentGuardStatus: 'POLICY SECURE',
    fraudGuardStatus: 'MEDIUM RISK',
    txnHash: '0x3C81B92019A8271C8819230018FA10',
    timestamp: '02:10:18 UTC',
    ipAddress: '198.51.100.42 (US-East)',
    metadata: { order_id: 'ORD-4412', channel: 'Direct', agent: 'AGT-441' },
  },
  {
    id: 'pay_2039C1d',
    amount: '$14,800.00',
    rawAmount: 14800.0,
    fee: '$0.00',
    net: '$0.00',
    status: 'FAILED',
    method: 'Offshore Wire Gateway',
    methodType: 'WIRE_TRANSFER',
    customerName: 'Unverified Overseas Vendor',
    customerEmail: 'transfer@wire-gateway.io',
    merchant: 'Unknown Gateway',
    description: 'International Wire Deposit',
    agentName: 'Logistics Agent #203',
    agentId: 'AGT-203',
    policy: 'AGP-MER-003',
    riskScore: 96,
    riskBand: 'CRITICAL',
    agentGuardStatus: 'POLICY VIOLATION',
    fraudGuardStatus: 'HIGH RISK',
    txnHash: '0x2A91D0018274A991028371982A8812',
    timestamp: '01:58:44 UTC',
    ipAddress: '45.142.214.8 (Panama Proxy)',
    metadata: { order_id: 'ORD-2039', flag: 'Sanctions Shield Breach', agent: 'AGT-203' },
  },
  {
    id: 'pay_1184D3e',
    amount: '$1,820.00',
    rawAmount: 1820.0,
    fee: '$52.80',
    net: '$1,767.20',
    status: 'SETTLED',
    method: 'Mastercard ****8812',
    methodType: 'MASTERCARD',
    customerName: 'United Corp Travel',
    customerEmail: 'travel@unitedcorp.com',
    merchant: 'United Airlines',
    description: 'Corporate Flight Booking #118',
    agentName: 'Travel Agent #118',
    agentId: 'AGT-118',
    policy: 'AGP-GOV-001',
    riskScore: 12,
    riskBand: 'LOW',
    agentGuardStatus: 'POLICY SECURE',
    fraudGuardStatus: 'CLEAN',
    txnHash: '0x7B12E8890281C99018274A99120098',
    timestamp: '01:45:10 UTC',
    ipAddress: '12.180.44.12 (Austin)',
    metadata: { order_id: 'ORD-1184', category: 'Travel', agent: 'AGT-118' },
  },
  {
    id: 'pay_7721E4f',
    amount: '$3,450.00',
    rawAmount: 3450.0,
    fee: '$0.00',
    net: '$0.00',
    status: 'REFUNDED',
    method: 'Maya 0918****112',
    methodType: 'MAYA',
    customerName: 'Logistics Supply Co',
    customerEmail: 'finance@logistics-co.com',
    merchant: 'Freight Logistics',
    description: 'Duplicate Freight Charge Reversal',
    agentName: 'Logistics Agent #203',
    agentId: 'AGT-203',
    policy: 'AGP-REF-001',
    riskScore: 5,
    riskBand: 'LOW',
    agentGuardStatus: 'POLICY SECURE',
    fraudGuardStatus: 'CLEAN',
    txnHash: '0x88910A9812739812A98123C771892B',
    timestamp: '01:20:05 UTC',
    ipAddress: '203.0.113.88 (Singapore)',
    metadata: { order_id: 'ORD-7721', refund_reason: 'Duplicate Charge', agent: 'AGT-203' },
  },
  {
    id: 'pay_5541F5g',
    amount: '$950.00',
    rawAmount: 950.0,
    fee: '$27.55',
    net: '$922.45',
    status: 'PENDING',
    method: 'Visa ****1092',
    methodType: 'VISA',
    customerName: 'Design Studio LLC',
    customerEmail: 'hello@designstudio.io',
    merchant: 'Creative Assets',
    description: 'Enterprise Design Asset Subscription',
    agentName: 'Design Operations Agent #554',
    agentId: 'AGT-554',
    policy: 'AGP-SUB-009',
    riskScore: 22,
    riskBand: 'LOW',
    agentGuardStatus: 'POLICY SECURE',
    fraudGuardStatus: 'LOW RISK',
    txnHash: '0x10928371928371928371982A109823',
    timestamp: '01:05:00 UTC',
    ipAddress: '198.51.100.99 (US-West)',
    metadata: { order_id: 'ORD-5541', plan: 'Enterprise', agent: 'AGT-554' },
  },
];

const INITIAL_WEBHOOKS: WebhookEventRecord[] = [
  {
    id: 'evt_9981A',
    event: 'PAYMENT.AUTHORIZED',
    paymentId: 'pay_9981A7b',
    status: 'DELIVERED',
    statusCode: 200,
    latency: '14ms',
    attempts: 1,
    timestamp: '02:14:22 UTC',
  },
  {
    id: 'evt_4412B',
    event: 'PAYMENT.CAPTURED',
    paymentId: 'pay_4412B9c',
    status: 'DELIVERED',
    statusCode: 200,
    latency: '18ms',
    attempts: 1,
    timestamp: '02:10:18 UTC',
  },
  {
    id: 'evt_2039C',
    event: 'PAYMENT.FAILED',
    paymentId: 'pay_2039C1d',
    status: 'DELIVERED',
    statusCode: 200,
    latency: '12ms',
    attempts: 1,
    timestamp: '01:58:44 UTC',
  },
  {
    id: 'evt_1184D',
    event: 'SETTLEMENT.CREATED',
    paymentId: 'po_8812A',
    status: 'DELIVERED',
    statusCode: 200,
    latency: '15ms',
    attempts: 1,
    timestamp: '01:45:10 UTC',
  },
];

const INITIAL_SETTLEMENTS: SettlementRecord[] = [
  {
    id: 'po_8812A',
    grossAmount: '$42,180.00',
    feeAmount: '-$1,265.40',
    netAmount: '$40,914.60',
    bankDestination: 'Chase Bank (••••4491)',
    status: 'SETTLED',
    payoutDate: '2026-08-29 23:00 UTC',
    txnCount: 142,
  },
  {
    id: 'po_7719B',
    grossAmount: '$28,450.00',
    feeAmount: '-$853.50',
    netAmount: '$27,596.50',
    bankDestination: 'Chase Bank (••••4491)',
    status: 'SETTLED',
    payoutDate: '2026-08-28 23:00 UTC',
    txnCount: 98,
  },
];

export default function ProductionPaymentsPage() {
  const [payments, setPayments] = useState<PaymentRecord[]>(INITIAL_PAYMENTS);
  const [webhooks] = useState<WebhookEventRecord[]>(INITIAL_WEBHOOKS);
  const [settlements] = useState<SettlementRecord[]>(INITIAL_SETTLEMENTS);

  const [activeTab, setActiveTab] = useState<PaymentTabType>('TRANSACTIONS');
  const [selectedPaymentId, setSelectedPaymentId] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [methodFilter, setMethodFilter] = useState<string>('ALL');
  const [dateFilter, setDateFilter] = useState<string>('24H');

  // Selected Payment Object
  const selectedPayment = useMemo(
    () => payments.find((p) => p.id === selectedPaymentId) || null,
    [payments, selectedPaymentId]
  );

  // Filtered Payments
  const filteredPayments = useMemo(() => {
    return payments.filter((p) => {
      if (statusFilter !== 'ALL' && p.status !== statusFilter) return false;
      if (methodFilter !== 'ALL' && !p.methodType.includes(methodFilter)) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        return (
          p.id.toLowerCase().includes(q) ||
          p.customerName.toLowerCase().includes(q) ||
          p.merchant.toLowerCase().includes(q) ||
          p.description.toLowerCase().includes(q) ||
          p.agentName.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [payments, statusFilter, methodFilter, searchQuery]);

  // Handle Actions
  const handleRefund = (id: string) => {
    setPayments((prev) =>
      prev.map((p) => (p.id === id ? { ...p, status: 'REFUNDED' as const } : p))
    );
  };

  const handleRetry = (id: string) => {
    setPayments((prev) =>
      prev.map((p) => (p.id === id ? { ...p, status: 'PROCESSING' as const } : p))
    );
  };

  const handleBlock = (id: string) => {
    setPayments((prev) =>
      prev.map((p) => (p.id === id ? { ...p, status: 'FAILED' as const } : p))
    );
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setStatusFilter('ALL');
    setMethodFilter('ALL');
    setDateFilter('24H');
  };

  return (
    <AgentPayShell activeTab="payments">
      <div className="space-y-6 pb-12">
        
        {/* PAGE HEADER */}
        <PaymentHeader
          onRefresh={() => {}}
          onExport={() => {}}
          onCreatePayment={() => {
            const newId = `pay_${Math.random().toString(36).substring(2, 9)}`;
            const newRecord: PaymentRecord = {
              id: newId,
              amount: '$1,500.00',
              rawAmount: 1500.0,
              fee: '$43.50',
              net: '$1,456.50',
              status: 'AUTHORIZED',
              method: 'Visa ****9981',
              methodType: 'VISA',
              customerName: 'New Corporate Agent',
              customerEmail: 'agent@agentpay.io',
              merchant: 'Cloud Operations',
              description: 'Instant Agent Spend Execution',
              agentName: 'Custom Agent #901',
              agentId: 'AGT-901',
              policy: 'AGP-SPEND-001',
              riskScore: 10,
              riskBand: 'LOW',
              agentGuardStatus: 'POLICY SECURE',
              fraudGuardStatus: 'CLEAN',
              txnHash: `0x${Math.random().toString(16).substring(2, 24)}`,
              timestamp: `${new Date().toISOString().substring(11, 19)} UTC`,
              ipAddress: '10.0.0.1 (VPN)',
              metadata: { order_id: 'ORD-NEW', agent: 'AGT-901' },
            };
            setPayments((prev) => [newRecord, ...prev]);
            setSelectedPaymentId(newId);
          }}
        />

        {/* METRICS GRID */}
        <PaymentMetrics
          grossVolume="$142,850.00"
          volumeTrend="+14.2%"
          successfulPayments={1284}
          successRate="94.2%"
          failedPayments={42}
          failureRate="3.1%"
          netPayout="$138,564.50"
        />

        {/* TABS SWITCHER */}
        <PaymentTabs activeTab={activeTab} onTabChange={setActiveTab} />

        {/* TAB 1: PAYMENTS & TRANSACTIONS */}
        {activeTab === 'TRANSACTIONS' && (
          <div className="space-y-4">
            <PaymentFilters
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              statusFilter={statusFilter}
              onStatusChange={setStatusFilter}
              methodFilter={methodFilter}
              onMethodChange={setMethodFilter}
              dateFilter={dateFilter}
              onDateChange={setDateFilter}
              onReset={handleResetFilters}
            />

            <PaymentTable
              payments={filteredPayments}
              selectedPaymentId={selectedPaymentId}
              onSelectPayment={(id) => setSelectedPaymentId(id)}
            />
          </div>
        )}

        {/* TAB 2: WEBHOOK & EVENT ACTIVITY */}
        {activeTab === 'WEBHOOKS' && <WebhookEvents events={webhooks} />}

        {/* TAB 3: CHECKOUT SESSION TESTER */}
        {activeTab === 'CHECKOUT_TESTER' && <CheckoutTester />}

        {/* TAB 4: SETTLEMENTS & PAYOUTS */}
        {activeTab === 'SETTLEMENTS' && <Settlements settlements={settlements} />}

        {/* PAYMENT INSPECTOR SLIDE-OVER DRAWER */}
        <PaymentInspector
          payment={selectedPayment}
          onClose={() => setSelectedPaymentId(null)}
          onRefund={handleRefund}
          onRetry={handleRetry}
          onBlock={handleBlock}
        />

      </div>
    </AgentPayShell>
  );
}
