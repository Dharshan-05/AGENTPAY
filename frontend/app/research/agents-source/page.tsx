'use client';

import { useState, useMemo } from 'react';
import './agents-source.css';
import { SourceHeader } from '@/components/research/agents/source-header';
import { SourceMetrics } from '@/components/research/agents/source-metrics';
import { SourceControls } from '@/components/research/agents/source-controls';
import { SourceTabs } from '@/components/research/agents/source-tabs';
import { SourceAgentRegistry } from '@/components/research/agents/source-agent-registry';
import { SourceAgentExecutions } from '@/components/research/agents/source-agent-executions';
import { SourceInspector } from '@/components/research/agents/source-inspector';

import {
  AgentSourceTabType,
  SourceAgentRecord,
  SourceAgentExecution,
} from '@/components/research/agents/source-types';

import {
  MOCK_SOURCE_AGENTS,
  MOCK_SOURCE_EXECUTIONS,
  MOCK_SOURCE_PERMISSIONS,
  MOCK_SOURCE_SECURITY,
} from '@/components/research/agents/source-data';

export default function AgentOperationsSourceResearchPage() {
  const [activeTab, setActiveTab] = useState<AgentSourceTabType>('REGISTRY');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedType, setSelectedType] = useState('ALL');
  const [selectedEnvironment, setSelectedEnvironment] = useState('ALL');

  // Inspector State
  const [selectedAgent, setSelectedAgent] = useState<SourceAgentRecord | null>(null);

  // Filtered Datasets
  const filteredAgents = useMemo(() => {
    return MOCK_SOURCE_AGENTS.filter((a) => {
      const matchSearch =
        !searchQuery ||
        a.agentId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.owner.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.policyBinding.toLowerCase().includes(searchQuery.toLowerCase());
      const matchStatus = selectedStatus === 'ALL' || a.status === selectedStatus;
      const matchType = selectedType === 'ALL' || a.type === selectedType;
      const matchEnv = selectedEnvironment === 'ALL' || a.environment === selectedEnvironment;
      return matchSearch && matchStatus && matchType && matchEnv;
    });
  }, [searchQuery, selectedStatus, selectedType, selectedEnvironment]);

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedStatus('ALL');
    setSelectedType('ALL');
    setSelectedEnvironment('ALL');
  };

  return (
    <div className="agents-source-root min-h-screen p-6 space-y-6 bg-slate-100 font-sans">
      
      {/* HEADER */}
      <SourceHeader
        onRefresh={() => alert('Telemetry feed refreshed')}
        onExport={() => alert('Exporting agent operations ledger')}
      />

      {/* METRICS */}
      <SourceMetrics />

      {/* CONTROLS */}
      <SourceControls
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedStatus={selectedStatus}
        onStatusChange={setSelectedStatus}
        selectedType={selectedType}
        onTypeChange={setSelectedType}
        selectedEnvironment={selectedEnvironment}
        onEnvironmentChange={setSelectedEnvironment}
        onReset={handleResetFilters}
      />

      {/* TABS */}
      <SourceTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {/* TAB CONTENTS */}
      {activeTab === 'REGISTRY' && (
        <SourceAgentRegistry
          agents={filteredAgents}
          onSelectAgent={(a) => setSelectedAgent(a)}
        />
      )}

      {activeTab === 'EXECUTIONS' && (
        <SourceAgentExecutions executions={MOCK_SOURCE_EXECUTIONS} />
      )}

      {activeTab === 'PERMISSIONS' && (
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
          <h3 className="font-bold text-slate-900 text-sm">RBAC Capabilities Matrix</h3>
          <div className="overflow-x-auto font-mono text-xs">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
                  <th className="p-3">Agent ID</th>
                  <th className="p-3">Resource Target</th>
                  <th className="p-3">Capability</th>
                  <th className="p-3">Permission Scope</th>
                  <th className="p-3">Policy Rule</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {MOCK_SOURCE_PERMISSIONS.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50">
                    <td className="p-3 font-bold text-blue-700">{p.agentId}</td>
                    <td className="p-3 font-bold text-slate-900">{p.resource}</td>
                    <td className="p-3 text-slate-700">{p.capability}</td>
                    <td className="p-3 font-bold text-emerald-600">{p.scope}</td>
                    <td className="p-3 text-slate-500 text-[10px]">{p.policyRule}</td>
                    <td className="p-3 font-bold text-emerald-600">{p.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'SECURITY' && (
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
          <h3 className="font-bold text-slate-900 text-sm">mTLS & Security Posture Log</h3>
          <div className="overflow-x-auto font-mono text-xs">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
                  <th className="p-3">Agent ID</th>
                  <th className="p-3">Credential Type</th>
                  <th className="p-3">mTLS Status</th>
                  <th className="p-3">Key Fingerprint</th>
                  <th className="p-3">Last Authentication</th>
                  <th className="p-3">Audit Hash</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {MOCK_SOURCE_SECURITY.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50">
                    <td className="p-3 font-bold text-blue-700">{s.agentId}</td>
                    <td className="p-3 font-bold text-slate-900">{s.credentialType}</td>
                    <td className="p-3 font-bold text-emerald-600">{s.mTLSCertificateStatus}</td>
                    <td className="p-3 text-slate-500 text-[10px]">{s.keyFingerprint}</td>
                    <td className="p-3 text-slate-700">{s.lastAuthTimestamp}</td>
                    <td className="p-3 text-slate-500 text-[10px] font-mono">{s.auditHash}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* INSPECTOR DRAWER */}
      <SourceInspector
        agent={selectedAgent}
        onClose={() => setSelectedAgent(null)}
      />

    </div>
  );
}
