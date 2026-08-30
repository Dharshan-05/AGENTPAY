'use client';

import React from 'react';
import { AgentPaySidebar } from './AgentPaySidebar';
import { AgentPayTopNav } from './AgentPayTopNav';

interface AgentPayShellProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  children: React.ReactNode;
}

export function AgentPayShell({ activeTab, onTabChange, children }: AgentPayShellProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex overflow-x-hidden font-sans selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Background Subtle Mesh */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-emerald-500/[0.03] rounded-full blur-[140px]" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-blue-500/[0.03] rounded-full blur-[140px]" />
      </div>

      {/* Persistent Master Sidebar */}
      <AgentPaySidebar activeTab={activeTab} onTabChange={onTabChange} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 z-10">
        <AgentPayTopNav />
        <main className="flex-1 p-6 md:p-8 overflow-y-auto max-w-[1600px] w-full mx-auto space-y-6">
          {children}
        </main>
      </div>
    </div>
  );
}
