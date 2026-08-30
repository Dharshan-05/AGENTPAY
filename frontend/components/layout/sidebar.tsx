'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  ShieldCheck,
  Terminal,
  LayoutDashboard,
  Bot,
  Shield,
  Cpu,
  CreditCard,
  BarChart3,
  Code2,
  Settings,
  ChevronLeft,
  ChevronRight,
  Radio,
} from 'lucide-react';

interface SidebarProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}

const NAV_ITEMS = [
  { id: 'command-center', name: 'COMMAND CENTER', icon: ShieldCheck, badge: 'LIVE', href: '/command-center' },
  { id: 'ai-command-center', name: 'AI COMMAND CENTER', icon: Terminal, badge: 'PAGE 003', href: '/ai-command-center' },
  { id: 'dashboard', name: 'DASHBOARD', icon: LayoutDashboard },
  { id: 'agents', name: 'AGENTS', icon: Bot, count: 6 },
  { id: 'agentguard', name: 'AGENTGUARD', icon: Shield, badge: 'POLICIES', href: '/agentguard' },
  { id: 'fraudguard', name: 'FRAUDGUARD', icon: Cpu, badge: 'AI RISK', href: '/fraudguard' },
  { id: 'payments', name: 'PAYMENTS', icon: CreditCard },
  { id: 'analytics', name: 'ANALYTICS', icon: BarChart3 },
  { id: 'developer', name: 'DEVELOPER', icon: Code2 },
  { id: 'settings', name: 'SETTINGS', icon: Settings },
];

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <aside
      className={`bg-slate-950/95 border-r border-white/[0.08] flex flex-col justify-between transition-all duration-300 z-30 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Top Logo & Collapse Button */}
      <div>
        <div className="h-16 px-5 border-b border-white/[0.08] flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0 group-hover:border-emerald-400/60 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.2)]">
              <ShieldCheck className="w-5 h-5" />
            </div>
            {!collapsed && (
              <span className="font-display font-bold text-base text-slate-100 tracking-wider">
                AGENT<span className="text-emerald-400">PAY</span>
              </span>
            )}
          </Link>

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="text-slate-500 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-900 transition-colors hidden md:block"
            aria-label="Toggle Sidebar"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Items */}
        <div className="p-3 space-y-1">
          {!collapsed && (
            <div className="px-3 py-2 text-[10px] font-mono tracking-[0.2em] text-slate-500 uppercase">
              Operational Modules
            </div>
          )}

          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isRouteActive = item.href ? pathname === item.href : activeTab === item.id;

            const content = (
              <>
                <Icon className={`w-4 h-4 shrink-0 ${isRouteActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                {!collapsed && <span className="truncate">{item.name}</span>}
                {!collapsed && item.badge && (
                  <span className="ml-auto px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[9px] font-mono border border-emerald-500/20">
                    {item.badge}
                  </span>
                )}
                {!collapsed && item.count !== undefined && (
                  <span className="ml-auto px-1.5 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px] font-mono">
                    {item.count}
                  </span>
                )}
              </>
            );

            const className = `w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-mono text-xs transition-all ${
              isRouteActive
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold shadow-[0_0_15px_rgba(16,185,129,0.15)]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            } ${collapsed ? 'justify-center' : ''}`;

            if (item.href) {
              return (
                <Link key={item.id} href={item.href} className={className} title={item.name}>
                  {content}
                </Link>
              );
            }

            return (
              <button
                key={item.id}
                onClick={() => onTabChange && onTabChange(item.id)}
                className={className}
                title={item.name}
              >
                {content}
              </button>
            );
          })}
        </div>
      </div>

      {/* Zero-Trust Status Footer */}
      {!collapsed && (
        <div className="p-4 m-3 rounded-xl bg-slate-900/60 border border-white/[0.06] text-xs font-mono">
          <div className="flex items-center gap-2 text-emerald-400 mb-1">
            <Radio className="w-3.5 h-3.5 animate-pulse" />
            <span className="font-bold text-[11px]">ZERO-TRUST ACTIVE</span>
          </div>
          <p className="text-[10px] text-slate-500">
            Node #01-US-EAST · 14ms latency
          </p>
        </div>
      )}
    </aside>
  );
}
