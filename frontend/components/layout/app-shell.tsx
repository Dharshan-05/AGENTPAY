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
    <div className="flex min-h-screen bg-[#020617] text-slate-100 font-sans selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Ambient Gradient Background Mesh */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute inset-0 bg-[#020617]" />
        <GradientMesh colors={['#10B981', '#3B82F6', '#6366F1']} intensity={0.03} />
      </div>

      <CursorFollower />

      {/* Persistent Left Navigation Sidebar */}
      <Sidebar activeTab={activeTab} onTabChange={onTabChange} />

      {/* Main Viewport Container */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header Bar */}
        <TopNav
          searchQuery={searchQuery}
          onSearchChange={onSearchChange}
          onEmergencyFreeze={onEmergencyFreeze}
        />

        {/* Page Content Body */}
        <main className="p-6 md:p-8 space-y-8 flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
