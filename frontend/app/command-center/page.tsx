'use client';

import { useState } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { MetricsGrid } from '@/components/command-center/metrics-grid';
import { LiveOperationsChart } from '@/components/command-center/operations-chart';
import { LiveStream, StreamEvent } from '@/components/command-center/live-stream';
import { AgentFleet, AgentItem } from '@/components/command-center/agent-fleet';
import { TransactionStreamTable } from '@/components/command-center/transaction-stream';
import { RiskInsights, InsightItem } from '@/components/command-center/risk-insights';
import { ApprovalsWidget, ApprovalItem } from '@/components/command-center/approvals-widget';
import { QuickActions } from '@/components/command-center/quick-actions';
import { AgentInspector } from '@/components/command-center/agent-inspector';
import { ShieldCheck, Plus, Radio, Zap } from 'lucide-react';

const INITIAL_AGENTS: AgentItem[] = [
  {
    id: 'agent_procure_892',
    name: 'Procurement Agent #892',
    role: 'Infrastructure & Hardware',
    tier: 'Tier-1 Autonomous',
    status: 'ACTIVE',
    dailySpend: 2480,
    dailyLimit: 5000,
    riskScore: 0.08,
    lastAction: 'Purchased AWS EC2 GPU Server instance ($2,480.00)',
    activePolicy: 'INFRA_SPEND_POLICY_V2',
    color: '#3B82F6',
  },
  {
    id: 'agent_travel_402',
    name: 'Travel Agent',
    role: 'Corporate Flight & Hotel Booking',
    tier: 'Tier-2 Guarded',
    status: 'ACTIVE',
    dailySpend: 1820,
    dailyLimit: 3000,
    riskScore: 0.05,
    lastAction: 'Booked United Airlines Flights for SecOps Summit ($1,820.00)',
    activePolicy: 'CORPORATE_TRAVEL_CAP',
    color: '#10B981',
  },
  {
    id: 'agent_shopping_109',
    name: 'Shopping Agent',
    role: 'Enterprise Vendor Purchasing',
    tier: 'Tier-1 Autonomous',
    status: 'PENDING_APPROVAL',
    dailySpend: 4820,
    dailyLimit: 5000,
    riskScore: 0.72,
    lastAction: 'Attempted Apple Store bulk hardware order ($4,820.00)',
    activePolicy: 'HARDWARE_WHITELIST_LIMIT',
    color: '#F59E0B',
  },
  {
    id: 'agent_finance_550',
    name: 'Finance Agent',
    role: 'Treasury & Cash Management',
    tier: 'Tier-1 Autonomous',
    status: 'ACTIVE',
    dailySpend: 8400,
    dailyLimit: 15000,
    riskScore: 0.03,
    lastAction: 'Transferred payroll liquidity to vault account ($8,400.00)',
    activePolicy: 'TREASURY_LIQUIDITY_V1',
    color: '#6366F1',
  },
  {
    id: 'agent_support_301',
    name: 'Support Agent',
    role: 'Customer Refund Disbursements',
    tier: 'Tier-3 HITL Required',
    status: 'ACTIVE',
    dailySpend: 150,
    dailyLimit: 1000,
    riskScore: 0.02,
    lastAction: 'Processed order return refund ($150.00)',
    activePolicy: 'REFUND_MAX_200_PER_TX',
    color: '#60A5FA',
  },
  {
    id: 'agent_logistics_007',
    name: 'Logistics Agent',
    role: 'Supply Chain Freight Orders',
    tier: 'Tier-2 Guarded',
    status: 'HIGH_RISK',
    dailySpend: 9200,
    dailyLimit: 10000,
    riskScore: 0.96,
    lastAction: 'Attempted unverified wire transfer to unknown routing ($9,200.00)',
    activePolicy: 'SUPPLY_CHAIN_WIRE_LOCK',
    color: '#EF4444',
  },
];

const INITIAL_EVENTS: StreamEvent[] = [
  {
    id: 'evt_1',
    timestamp: '12:48:22 UTC',
    agentName: 'Procurement Agent #892',
    agentId: 'agent_procure_892',
    intent: 'AWS EC2 GPU Cluster Purchase',
    amount: 2480,
    policyResult: 'APPROVED',
    riskScore: 0.08,
    hash: '0x8F9A2B1C',
  },
  {
    id: 'evt_2',
    timestamp: '12:47:02 UTC',
    agentName: 'Logistics Agent',
    agentId: 'agent_logistics_007',
    intent: 'Unverified Overseas Wire Transfer',
    amount: 9200,
    policyResult: 'DENIED',
    riskScore: 0.96,
    hash: '0x3E1A9C5D',
  },
];

const INITIAL_INSIGHTS: InsightItem[] = [
  {
    id: 'ins_1',
    type: 'SECURITY_ALERT',
    title: 'Adversarial Prompt Injection Blocked',
    desc: 'Logistics Agent attempted wire transfer to unverified routing number.',
    recommendation: 'Enforce strict beneficiary verification policy.',
    targetAgent: 'Logistics Agent',
    savingsOrRisk: '$9,200 High Risk Defended',
  },
  {
    id: 'ins_2',
    type: 'WARNING',
    title: 'Spend Velocity Breach Imminent',
    desc: 'Shopping Agent reached 96% of daily spend limit ($4,820 / $5,000).',
    recommendation: 'Require Human-in-the-Loop escalation.',
    targetAgent: 'Shopping Agent',
    savingsOrRisk: 'Cap Breach Prevented',
  },
];

const INITIAL_APPROVALS: ApprovalItem[] = [
  {
    id: 'app_1',
    agentName: 'Procurement Agent #892',
    intent: 'AWS EC2 Server Cluster ($2,480.00)',
    amount: 2480,
    time: '12:48:22 UTC',
    status: 'APPROVED',
    reason: 'Rule #INFRA_SPEND Passed (Budget < $5,000)',
  },
  {
    id: 'app_2',
    agentName: 'Logistics Agent',
    intent: 'Unverified Wire Transfer ($9,200.00)',
    amount: 9200,
    time: '12:47:02 UTC',
    status: 'BLOCKED',
    reason: 'FRAUDGUARD Anomaly Score 0.96 > 0.40 Threshold',
  },
];

export default function CommandCenterPage() {
  const [agents, setAgents] = useState<AgentItem[]>(INITIAL_AGENTS);
  const [events, setEvents] = useState<StreamEvent[]>(INITIAL_EVENTS);
  const [insights, setInsights] = useState<InsightItem[]>(INITIAL_INSIGHTS);
  const [approvals, setApprovals] = useState<ApprovalItem[]>(INITIAL_APPROVALS);
  const [selectedAgent, setSelectedAgent] = useState<AgentItem | null>(null);

  const handleDeployAgent = () => {
    const newId = `agent_custom_${Date.now().toString().slice(-3)}`;
    const newAgent: AgentItem = {
      id: newId,
      name: `Custom Agent #${newId.slice(-3)}`,
      role: 'Autonomous Micro-tasking',
      tier: 'Tier-1 Autonomous',
      status: 'ACTIVE',
      dailySpend: 0,
      dailyLimit: 2500,
      riskScore: 0.01,
      lastAction: 'Deployed to Mainnet execution pool',
      activePolicy: 'DEFAULT_MINT_LIMIT',
      color: '#10B981',
    };
    setAgents([newAgent, ...agents]);
  };

  const handleApproveAction = (approvalId: string) => {
    setApprovals(approvals.map((a) => (a.id === approvalId ? { ...a, status: 'APPROVED' } : a)));
  };

  const handleRejectAction = (approvalId: string) => {
    setApprovals(approvals.map((a) => (a.id === approvalId ? { ...a, status: 'BLOCKED' } : a)));
  };

  return (
    <AgentPayShell activeTab="command-center">
      <div className="space-y-6">
        <PageHeader
          eyebrow="COMMAND CENTER"
          title="OPERATIONS &"
          highlightTitle="AGENT FLEET"
          description="Real-time control tower monitoring autonomous AI agents, payment authorization velocity, and zero-trust policy enforcement."
          icon={ShieldCheck}
          statusBadge={<AGBadge status="LIVE" label="OPERATIONAL" />}
          actions={
            <>
              <AGButton variant="primary" icon={Plus} onClick={handleDeployAgent}>
                Deploy Agent
              </AGButton>
              <AGButton variant="secondary" icon={Zap}>
                Run Fleet Audit
              </AGButton>
            </>
          }
        />

        {/* Operational Metrics */}
        <MetricsGrid
          totalVolume={148920.00}
          activeAgents={agents.filter((a) => a.status === 'ACTIVE').length}
          totalAgents={agents.length}
          complianceRate={98.4}
          riskIndex={0.08}
        />

        {/* Live Operations & Stream */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <LiveOperationsChart />
          </div>
          <div>
            <LiveStream events={events} />
          </div>
        </div>

        {/* Agent Fleet Grid */}
        <AgentFleet
          agents={agents}
          selectedAgentId={selectedAgent ? selectedAgent.id : null}
          onSelectAgent={(agent) => setSelectedAgent(agent)}
        />

        {/* Transaction Stream Table */}
        <TransactionStreamTable events={events} onSelectEvent={() => {}} />

        {/* Insights & Approvals Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RiskInsights insights={insights} onApplyRecommendation={() => {}} />
          <ApprovalsWidget items={approvals} />
        </div>

        {/* Quick Actions Footer */}
        <QuickActions
          onAddAgent={handleDeployAgent}
          onNewPolicy={() => {}}
          onRefreshData={() => {}}
          onToggleFreeze={() => {}}
        />

        {/* Agent Inspector Slide-over */}
        <AgentInspector
          agent={selectedAgent}
          onClose={() => setSelectedAgent(null)}
          onUpdateLimit={() => {}}
          onToggleStatus={() => {}}
        />
      </div>
    </AgentPayShell>
  );
}
