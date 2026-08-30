'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { AgentHeader } from '@/components/agents/agent-header';
import { AgentMetrics } from '@/components/agents/agent-metrics';
import { AgentControls } from '@/components/agents/agent-controls';
import { AgentTabs } from '@/components/agents/agent-tabs';
import { AgentRegistryTable } from '@/components/agents/agent-registry-table';
import { AgentExecutionsTable } from '@/components/agents/agent-executions-table';
import { AgentPermissionsTable } from '@/components/agents/agent-permissions-table';
import { AgentSecurityTable } from '@/components/agents/agent-security-table';
import { AgentInspector } from '@/components/agents/agent-inspector';
import { RegisterAgentModal } from '@/components/agents/register-agent-modal';

import {
  AgentTabType,
  ProductionAgentRecord,
  ProductionAgentExecution,
  ProductionAgentPermissionRecord,
  ProductionAgentSecurityRecord,
} from '@/components/agents/agent-types';

import {
  INITIAL_PRODUCTION_AGENTS,
  INITIAL_PRODUCTION_EXECUTIONS,
  INITIAL_PRODUCTION_PERMISSIONS,
  INITIAL_PRODUCTION_SECURITY,
} from '@/components/agents/agent-data';

export default function ProductionAgentRegistryPage() {
  const [activeTab, setActiveTab] = useState<AgentTabType>('REGISTRY');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedType, setSelectedType] = useState('ALL');
  const [selectedEnvironment, setSelectedEnvironment] = useState('ALL');
  const [selectedRisk, setSelectedRisk] = useState('ALL');

  // State
  const [agents, setAgents] = useState<ProductionAgentRecord[]>(INITIAL_PRODUCTION_AGENTS);
  const [executions] = useState<ProductionAgentExecution[]>(INITIAL_PRODUCTION_EXECUTIONS);
  const [permissions] = useState<ProductionAgentPermissionRecord[]>(INITIAL_PRODUCTION_PERMISSIONS);
  const [securityRecords] = useState<ProductionAgentSecurityRecord[]>(INITIAL_PRODUCTION_SECURITY);

  // Inspector & Modal State
  const [selectedAgent, setSelectedAgent] = useState<ProductionAgentRecord | null>(null);
  const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);

  // Filtered Datasets
  const filteredAgents = useMemo(() => {
    return agents.filter((a) => {
      const matchSearch =
        !searchQuery ||
        a.agentId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.owner.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.policyBinding.toLowerCase().includes(searchQuery.toLowerCase());
      const matchStatus = selectedStatus === 'ALL' || a.status === selectedStatus;
      const matchType = selectedType === 'ALL' || a.type === selectedType;
      const matchEnv = selectedEnvironment === 'ALL' || a.environment === selectedEnvironment;
      const matchRisk = selectedRisk === 'ALL' || a.riskTier === selectedRisk;
      return matchSearch && matchStatus && matchType && matchEnv && matchRisk;
    });
  }, [agents, searchQuery, selectedStatus, selectedType, selectedEnvironment, selectedRisk]);

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedStatus('ALL');
    setSelectedType('ALL');
    setSelectedEnvironment('ALL');
    setSelectedRisk('ALL');
  };

  const handleRegisterSuccess = (agentName: string, agentType: string) => {
    const newId = `AGT-${Math.floor(100 + Math.random() * 900)}`;
    const newAgent: ProductionAgentRecord = {
      id: `agt_new_${Date.now()}`,
      agentId: newId,
      name: agentName,
      type: agentType as any,
      owner: 'Finance Operations',
      environment: 'PRODUCTION',
      status: 'ACTIVE',
      riskTier: 'LOW',
      policyBinding: 'AGP-GOV-001 (Micro-Payments)',
      lastActive: 'Just now',
      transactionCount: 0,
      healthScore: 100,
      credentialRotationDays: 30,
    };
    setAgents([newAgent, ...agents]);
    alert(`Zero-Trust Identity ${newId} registered successfully.`);
  };

  return (
    <AgentPayShell activeTab="agents">
      <div className="space-y-6 pb-12">
        
        {/* HEADER */}
        <AgentHeader
          onRefresh={() => alert('Agent operations telemetry feed refreshed')}
          onExport={() => alert('Exporting cryptographic agent identity ledger...')}
          onRegister={() => setIsRegisterModalOpen(true)}
        />

        {/* METRICS */}
        <AgentMetrics
          registeredAgentsCount={agents.length}
          activeAgentsCount={agents.filter((a) => a.status === 'ACTIVE').length}
          executions24h="142,890"
          suspendedCount={agents.filter((a) => a.status === 'SUSPENDED').length}
          rotationsDueCount={2}
        />

        {/* CONTROLS */}
        <AgentControls
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedStatus={selectedStatus}
          onStatusChange={setSelectedStatus}
          selectedType={selectedType}
          onTypeChange={setSelectedType}
          selectedEnvironment={selectedEnvironment}
          onEnvironmentChange={setSelectedEnvironment}
          selectedRisk={selectedRisk}
          onRiskChange={setSelectedRisk}
          onReset={handleResetFilters}
        />

        {/* TABS */}
        <AgentTabs activeTab={activeTab} onTabChange={setActiveTab} />

        {/* TAB 1: REGISTRY */}
        {activeTab === 'REGISTRY' && (
          <AgentRegistryTable
            agents={filteredAgents}
            onSelectAgent={(a) => setSelectedAgent(a)}
          />
        )}

        {/* TAB 2: EXECUTIONS */}
        {activeTab === 'EXECUTIONS' && (
          <AgentExecutionsTable executions={executions} />
        )}

        {/* TAB 3: PERMISSIONS */}
        {activeTab === 'PERMISSIONS' && (
          <AgentPermissionsTable permissions={permissions} />
        )}

        {/* TAB 4: SECURITY */}
        {activeTab === 'SECURITY' && (
          <AgentSecurityTable securityRecords={securityRecords} />
        )}

        {/* AGENT INSPECTOR DRAWER */}
        <AgentInspector
          agent={selectedAgent}
          onClose={() => setSelectedAgent(null)}
        />

        {/* REGISTER AGENT MODAL */}
        <RegisterAgentModal
          isOpen={isRegisterModalOpen}
          onClose={() => setIsRegisterModalOpen(false)}
          onRegisterSuccess={handleRegisterSuccess}
        />

      </div>
    </AgentPayShell>
  );
}
