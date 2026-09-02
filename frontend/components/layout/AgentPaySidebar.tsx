'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  ShieldCheck,
  Terminal,
  Bot,
  Shield,
  Cpu,
  CreditCard,
  BarChart3,
  Code2,
  Settings,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Radio,
  Receipt,
  Users,
  Building2,
  RotateCcw,
  AlertCircle,
  Landmark,
  ArrowUpRight,
  FileText,
  Repeat,
  Layers,
  Search,
  Link2,
  ShoppingBag,
  RefreshCw,
  FileCode,
  Wallet,
  Network,
  Percent,
  Building,
  ShieldAlert,
  Bell,
  FileCheck,
  Coins,
  Activity,
  Package,
  ShoppingCart,
  ListOrdered,
  Boxes,
  Clock,
  Truck,
  Scale,
  MapPin,
  KeyRound,
  Zap,
  Tag,
  Ticket,
  Gift,
  Award,
  ListFilter,
  UserCheck,
  Plug,
  Server,
  Key,
  AlertTriangle,
  Lock,
} from 'lucide-react';

interface SidebarProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}

interface NavItem {
  id: string;
  name: string;
  icon: any;
  href?: string;
  badge?: string;
  count?: number;
}

interface NavGroup {
  id: string;
  title: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    id: 'command-center',
    title: 'COMMAND CENTER',
    items: [
      { id: 'command-center', name: 'COMMAND CENTER', icon: ShieldCheck, badge: 'LIVE', href: '/command-center' },
      { id: 'ai-command-center', name: 'AI COMMAND CENTER', icon: Terminal, badge: 'AI', href: '/ai-command-center' },
    ],
  },
  {
    id: 'operations',
    title: 'OPERATIONS',
    items: [
      { id: 'agents', name: 'AGENTS', icon: Bot, count: 6, href: '/agents' },
      { id: 'transactions', name: 'TRANSACTIONS', icon: Receipt, href: '/transactions' },
      { id: 'webhooks', name: 'WEBHOOKS', icon: Radio, href: '/webhooks' },
      { id: 'payment-methods', name: 'PAYMENT METHODS', icon: CreditCard, href: '/payment-methods' },
      { id: 'customers', name: 'CUSTOMERS', icon: Users, href: '/customers' },
      { id: 'merchants', name: 'MERCHANTS', icon: Building2, href: '/merchants' },
      { id: 'payment-intents', name: 'PAYMENT INTENTS', icon: Receipt, href: '/payment-intents' },
      { id: 'payment-links', name: 'PAYMENT LINKS', icon: Link2, href: '/payment-links' },
      { id: 'checkout', name: 'CHECKOUT', icon: ShoppingBag, href: '/checkout' },
      { id: 'mandates', name: 'MANDATES', icon: ShieldCheck, href: '/mandates' },
      { id: 'recurring-payments', name: 'RECURRING PAYMENTS', icon: RefreshCw, href: '/recurring-payments' },
      { id: 'contracts', name: 'SMART CONTRACTS', icon: FileCode, href: '/contracts' },
      { id: 'wallets', name: 'TREASURY WALLETS', icon: Wallet, href: '/wallets' },
      { id: 'gateways', name: 'PAYMENT GATEWAYS', icon: Network, href: '/gateways' },
    ],
  },
  {
    id: 'finance',
    title: 'FINANCE',
    items: [
      { id: 'refunds', name: 'REFUNDS', icon: RotateCcw, href: '/refunds' },
      { id: 'disputes', name: 'DISPUTES', icon: AlertCircle, href: '/disputes' },
      { id: 'settlements', name: 'SETTLEMENTS', icon: Landmark, href: '/settlements' },
      { id: 'payouts', name: 'PAYOUTS', icon: ArrowUpRight, href: '/payouts' },
      { id: 'ledger', name: 'FINANCIAL LEDGER', icon: FileText, href: '/ledger' },
      { id: 'subscriptions', name: 'SUBSCRIPTIONS', icon: Repeat, href: '/subscriptions' },
      { id: 'invoices', name: 'INVOICES', icon: FileText, href: '/invoices' },
      { id: 'billing', name: 'BILLING', icon: CreditCard, href: '/billing' },
      { id: 'plans', name: 'PLANS', icon: Layers, href: '/plans' },
      { id: 'fees', name: 'FEE & COMMISSION', icon: Percent, href: '/fees' },
      { id: 'taxes', name: 'TAX & COMPLIANCE', icon: Building, href: '/taxes' },
    ],
  },
  {
    id: 'security-risk',
    title: 'SECURITY & RISK',
    items: [
      { id: 'agentguard', name: 'AGENTGUARD', icon: Shield, badge: 'POLICIES', href: '/agentguard' },
      { id: 'fraudguard', name: 'FRAUDGUARD', icon: Cpu, badge: 'AI RISK', href: '/fraudguard' },
      { id: 'risk-rules', name: 'RISK RULES', icon: Cpu, href: '/risk-rules' },
      { id: 'approvals', name: 'HUMAN APPROVALS', icon: ShieldCheck, href: '/approvals' },
      { id: 'audit-logs', name: 'AUDIT LOGS', icon: ShieldAlert, href: '/audit-logs' },
      { id: 'compliance', name: 'AML & COMPLIANCE', icon: FileCheck, href: '/compliance' },
      { id: 'tokenization-vault', name: 'TOKEN VAULT', icon: Lock, href: '/tokenization-vault' },
      { id: '3ds-authentication', name: '3DS AUTHENTICATION', icon: ShieldCheck, href: '/3ds-authentication' },
    ],
  },
  {
    id: 'ai-intelligence',
    title: 'AI & INTELLIGENCE',
    items: [
      { id: 'ai-buyer', name: 'AI BUYER', icon: Bot, badge: 'BUYER', href: '/ai-command-center' },
      { id: 'products', name: 'PRODUCT SEARCH', icon: Package, href: '/products' },
      { id: 'orders', name: 'ORDERS', icon: ShoppingCart, href: '/orders' },
      { id: 'inventory', name: 'INVENTORY', icon: Boxes, href: '/inventory' },
      { id: 'analytics', name: 'ANALYTICS', icon: BarChart3, href: '/analytics' },
      { id: 'system-telemetry', name: 'SYSTEM TELEMETRY', icon: Activity, href: '/system-telemetry' },
    ],
  },
  {
    id: 'administration',
    title: 'ADMINISTRATION',
    items: [
      { id: 'api-keys', name: 'API KEYS & DEVS', icon: Key, href: '/api-keys' },
      { id: 'developers', name: 'DEVELOPER DOCS', icon: Code2, href: '/developers' },
      { id: 'settings', name: 'SETTINGS', icon: Settings, href: '/settings' },
      { id: 'login', name: 'AUTH / LOGIN', icon: Lock, badge: 'SSO', href: '/login' },
    ],
  },
];

export function AgentPaySidebar({ activeTab, onTabChange }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  // Collapsible state for each navigation group
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>(() => {
    const initialState: Record<string, boolean> = {
      'command-center': true,
      'operations': true,
      'finance': true,
      'security-risk': true,
      'ai-intelligence': true,
      'administration': true,
    };
    return initialState;
  });

  // Auto-expand group containing current route
  useEffect(() => {
    NAV_GROUPS.forEach((group) => {
      const containsActive = group.items.some(
        (item) => (item.href && pathname === item.href) || (activeTab && item.id === activeTab)
      );
      if (containsActive) {
        setOpenGroups((prev) => ({ ...prev, [group.id]: true }));
      }
    });
  }, [pathname, activeTab]);

  const toggleGroup = (groupId: string) => {
    setOpenGroups((prev) => ({ ...prev, [groupId]: !prev[groupId] }));
  };

  return (
    <aside
      className={`bg-slate-950/95 border-r border-white/[0.08] flex flex-col justify-between transition-all duration-300 z-30 shrink-0 h-full overflow-y-auto ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Top Logo & Collapse Toggle */}
      <div>
        <div className="h-16 px-5 border-b border-white/[0.08] flex items-center justify-between sticky top-0 bg-slate-950/95 z-10 backdrop-blur-md">
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

        {/* Collapsible Navigation Groups */}
        <div className="p-3 space-y-3">
          {NAV_GROUPS.map((group) => {
            const isGroupOpen = openGroups[group.id] ?? true;
            const hasActiveChild = group.items.some(
              (item) => (item.href && pathname === item.href) || (activeTab && item.id === activeTab)
            );

            return (
              <div key={group.id} className="space-y-1">
                {!collapsed ? (
                  <button
                    onClick={() => toggleGroup(group.id)}
                    className={`w-full flex items-center justify-between px-3 py-1.5 text-[10px] font-mono tracking-[0.15em] uppercase font-bold transition-colors ${
                      hasActiveChild ? 'text-emerald-400' : 'text-slate-500 hover:text-slate-300'
                    }`}
                  >
                    <span>{group.title}</span>
                    {isGroupOpen ? (
                      <ChevronDown className="w-3.5 h-3.5 opacity-70" />
                    ) : (
                      <ChevronRight className="w-3.5 h-3.5 opacity-70" />
                    )}
                  </button>
                ) : (
                  <div className="h-px bg-white/[0.06] my-2" />
                )}

                {(isGroupOpen || collapsed) && (
                  <div className="space-y-1">
                    {group.items.map((item) => {
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

                      const className = `w-full flex items-center gap-3 px-3 py-2 rounded-xl font-mono text-xs transition-all ${
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
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Zero-Trust Status Footer */}
      {!collapsed && (
        <div className="p-4 m-3 rounded-xl bg-slate-900/60 border border-white/[0.06] text-xs font-mono shrink-0">
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
