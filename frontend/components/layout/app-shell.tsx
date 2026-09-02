'use client';

import React, { useState } from 'react';
import { Sidebar } from './sidebar';
import { TopNav } from './topnav';
import { GradientMesh } from '@/components/motion/gradient-mesh';
import { CursorFollower } from '@/components/motion/cursor-follower';

interface AppShellProps {
  children: React.ReactNode;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
  onEmergencyFreeze?: () => void;
}

export function AppShell({
  children,
  activeTab = 'command-center',
  onTabChange = () => {},
  searchQuery = '',
  onSearchChange = () => {},
  onEmergencyFreeze = () => {},
}: AppShellProps) {
  return (
    <div className="h-screen w-screen overflow-hidden bg-[#020617] text-slate-100 font-sans flex flex-col selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Ambient Gradient Background Mesh */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute inset-0 bg-[#020617]" />
        <GradientMesh colors={['#10B981', '#3B82F6', '#6366F1']} intensity={0.03} />
      </div>

      <CursorFollower />

      {/* Top Header Bar */}
      <div className="shrink-0 z-20">
        <TopNav
          searchQuery={searchQuery}
          onSearchChange={onSearchChange}
          onEmergencyFreeze={onEmergencyFreeze}
        />
      </div>

      {/* Main Viewport Shell Split */}
      <div className="flex flex-1 min-h-0 min-w-0 overflow-hidden relative z-10">
        {/* Persistent Left Navigation Sidebar */}
        <Sidebar activeTab={activeTab} onTabChange={onTabChange} />

        {/* Page Content Body */}
        <main className="flex-1 h-full overflow-y-auto p-6 md:p-8 space-y-8">{children}</main>
      </div>
    </div>
  );
}

