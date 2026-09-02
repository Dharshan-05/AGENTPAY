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
    <div className="h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Background Subtle Mesh */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-emerald-500/[0.03] rounded-full blur-[140px]" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-blue-500/[0.03] rounded-full blur-[140px]" />
      </div>

      {/* Top Header Bar */}
      <div className="shrink-0 z-20">
        <AgentPayTopNav />
      </div>

      {/* Main Viewport Shell Split */}
      <div className="flex flex-1 min-h-0 min-w-0 overflow-hidden relative z-10">
        {/* Independent Left Navigation Sidebar */}
        <AgentPaySidebar activeTab={activeTab} onTabChange={onTabChange} />

        {/* Independent Main Content Area */}
        <main className="flex-1 h-full overflow-y-auto p-6 md:p-8 max-w-[1600px] w-full mx-auto space-y-6">
          {children}
        </main>
      </div>
    </div>
  );
}

