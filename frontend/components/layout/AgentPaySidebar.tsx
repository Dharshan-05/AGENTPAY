'use client';

import { useState } from 'react';
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
  group: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    group: 'COMMAND CENTER',
    items: [
      { id: 'command-center', name: 'COMMAND CENTER', icon: ShieldCheck, badge: 'LIVE', href: '/command-center' },
      { id: 'ai-command-center', name: 'AI COMMAND CENTER', icon: Terminal, badge: 'PAGE 003', href: '/ai-command-center' },
    ],
  },
  {
    group: 'OPERATIONS',
    items: [
      { id: 'agents', name: 'AGENTS', icon: Bot, count: 6, href: '/agents' },
      { id: 'transactions', name: 'TRANSACTIONS', icon: Receipt, badge: '012', href: '/transactions' },
      { id: 'webhooks', name: 'WEBHOOKS', icon: Radio, badge: '013', href: '/webhooks' },
      { id: 'payment-methods', name: 'PAYMENT METHODS', icon: CreditCard, badge: '014', href: '/payment-methods' },
      { id: 'customers', name: 'CUSTOMERS', icon: Users, badge: '015', href: '/customers' },
      { id: 'merchants', name: 'MERCHANTS', icon: Building2, badge: '016', href: '/merchants' },
      { id: 'payment-intents', name: 'PAYMENT INTENTS', icon: Receipt, badge: '017', href: '/payment-intents' },
      { id: 'refunds', name: 'REFUNDS', icon: RotateCcw, badge: '018', href: '/refunds' },
      { id: 'disputes', name: 'DISPUTES', icon: AlertCircle, badge: '019', href: '/disputes' },
      { id: 'settlements', name: 'SETTLEMENTS', icon: Landmark, badge: '020', href: '/settlements' },
      { id: 'payouts', name: 'PAYOUTS', icon: ArrowUpRight, badge: '021', href: '/payouts' },
      { id: 'ledger', name: 'FINANCIAL LEDGER', icon: FileText, badge: '022', href: '/ledger' },
      { id: 'subscriptions', name: 'SUBSCRIPTIONS', icon: Repeat, badge: '025', href: '/subscriptions' },
      { id: 'invoices', name: 'INVOICES', icon: FileText, badge: '026', href: '/invoices' },
      { id: 'billing', name: 'BILLING', icon: CreditCard, badge: '027', href: '/billing' },
      { id: 'plans', name: 'PLANS', icon: Layers, badge: '028', href: '/plans' },
      { id: 'customer-segments', name: 'CUSTOMER SEGMENTS', icon: Users, badge: '029', href: '/customer-segments' },
      { id: 'transaction-search', name: 'TRANSACTION SEARCH', icon: Search, badge: '030', href: '/transaction-search' },
      { id: 'payment-links', name: 'PAYMENT LINKS', icon: Link2, badge: '031', href: '/payment-links' },
      { id: 'checkout', name: 'CHECKOUT', icon: ShoppingBag, badge: '032', href: '/checkout' },
      { id: 'mandates', name: 'MANDATES', icon: ShieldCheck, badge: '033', href: '/mandates' },
      { id: 'recurring-payments', name: 'RECURRING PAYMENTS', icon: RefreshCw, badge: '034', href: '/recurring-payments' },
      { id: 'contracts', name: 'SMART CONTRACTS', icon: FileCode, badge: '035', href: '/contracts' },
      { id: 'wallets', name: 'TREASURY WALLETS', icon: Wallet, badge: '036', href: '/wallets' },
      { id: 'gateways', name: 'PAYMENT GATEWAYS', icon: Network, badge: '037', href: '/gateways' },
      { id: 'fees', name: 'FEE & COMMISSION', icon: Percent, badge: '038', href: '/fees' },
      { id: 'taxes', name: 'TAX & COMPLIANCE', icon: Building, badge: '039', href: '/taxes' },
      { id: 'notifications', name: 'NOTIFICATIONS', icon: Bell, badge: '041', href: '/notifications' },
      { id: 'fx-rates', name: 'FX RATES', icon: Coins, badge: '043', href: '/fx-rates' },
      { id: 'products', name: 'PRODUCTS', icon: Package, badge: '045', href: '/products' },
      { id: 'orders', name: 'ORDERS', icon: ShoppingCart, badge: '046', href: '/orders' },
      { id: 'order-items', name: 'ORDER ITEMS', icon: ListOrdered, badge: '047', href: '/order-items' },
      { id: 'inventory', name: 'INVENTORY', icon: Boxes, badge: '048', href: '/inventory' },
      { id: 'inventory-reservations', name: 'RESERVATIONS', icon: Clock, badge: '049', href: '/inventory-reservations' },
      { id: 'shipping', name: 'SHIPPING', icon: Truck, badge: '050', href: '/shipping' },
      { id: 'shipping-rates', name: 'SHIPPING RATES', icon: Scale, badge: '051', href: '/shipping-rates' },
      { id: 'addresses', name: 'ADDRESSES', icon: MapPin, badge: '052', href: '/addresses' },
      { id: 'sessions', name: 'CHECKOUT SESSIONS', icon: KeyRound, badge: '053', href: '/sessions' },
      { id: 'payment-attempts', name: 'PAYMENT ATTEMPTS', icon: Zap, badge: '054', href: '/payment-attempts' },
      { id: 'discounts', name: 'DISCOUNTS', icon: Tag, badge: '055', href: '/discounts' },
      { id: 'coupons', name: 'COUPONS', icon: Ticket, badge: '056', href: '/coupons' },
      { id: 'gift-cards', name: 'GIFT CARDS', icon: Gift, badge: '057', href: '/gift-cards' },
      { id: 'loyalty', name: 'LOYALTY & REWARDS', icon: Award, badge: '058', href: '/loyalty' },
      { id: 'store-credit', name: 'STORE CREDIT', icon: Coins, badge: '059', href: '/store-credit' },
      { id: 'returns', name: 'PRODUCT RETURNS', icon: RotateCcw, badge: '060', href: '/returns' },
      { id: 'exchanges', name: 'ITEM EXCHANGES', icon: Repeat, badge: '061', href: '/exchanges' },
      { id: 'supplier-payouts', name: 'SUPPLIER PAYOUTS', icon: Building2, badge: '062', href: '/supplier-payouts' },
      { id: 'commissions', name: 'COMMISSIONS', icon: Percent, badge: '063', href: '/commissions' },
      { id: 'tax-rates', name: 'TAX RATES', icon: Building, badge: '064', href: '/tax-rates' },
      { id: 'product-catalog', name: 'PRODUCT CATALOG', icon: Layers, badge: '065', href: '/product-catalog' },
      { id: 'order-management', name: 'ORDER MANAGEMENT', icon: ShoppingBag, badge: '066', href: '/order-management' },
      { id: 'order-item-breakdown', name: 'ITEM BREAKDOWN', icon: ListFilter, badge: '067', href: '/order-item-breakdown' },
      { id: 'inventory-control', name: 'INVENTORY CONTROL', icon: Boxes, badge: '068', href: '/inventory-control' },
      { id: 'stock-reservations', name: 'STOCK RESERVATIONS', icon: Clock, badge: '069', href: '/stock-reservations' },
      { id: 'shipment-dispatch', name: 'SHIPMENT DISPATCH', icon: Truck, badge: '070', href: '/shipment-dispatch' },
      { id: 'rate-matrices', name: 'RATE MATRICES', icon: Scale, badge: '071', href: '/rate-matrices' },
      { id: 'address-verification', name: 'ADDRESS VERIFICATION', icon: MapPin, badge: '072', href: '/address-verification' },
      { id: 'session-control', name: 'SESSION CONTROL', icon: KeyRound, badge: '073', href: '/session-control' },
      { id: 'payment-attempt-logs', name: 'ATTEMPT LOGS', icon: Zap, badge: '074', href: '/payment-attempt-logs' },
      { id: 'chargebacks', name: 'CHARGEBACKS', icon: AlertCircle, badge: '075', href: '/chargebacks' },
      { id: 'settlement-reconciliation', name: 'SETTLEMENT RECON', icon: Landmark, badge: '076', href: '/settlement-reconciliation' },
      { id: 'payout-schedules', name: 'PAYOUT SCHEDULES', icon: ArrowUpRight, badge: '077', href: '/payout-schedules' },
      { id: 'sub-merchants', name: 'SUB-MERCHANTS', icon: Building2, badge: '078', href: '/sub-merchants' },
      { id: 'gateway-routing', name: 'GATEWAY ROUTING', icon: Network, badge: '079', href: '/gateway-routing' },
      { id: 'fee-structures', name: 'FEE STRUCTURES', icon: Percent, badge: '080', href: '/fee-structures' },
      { id: 'tax-jurisdictions', name: 'TAX JURISDICTIONS', icon: Building, badge: '081', href: '/tax-jurisdictions' },
      { id: 'audit-trails', name: 'AUDIT TRAILS', icon: FileCode, badge: '082', href: '/audit-trails' },
      { id: 'fx-exchanges', name: 'FX EXCHANGES', icon: Coins, badge: '083', href: '/fx-exchanges' },
      { id: 'system-telemetry', name: 'SYSTEM TELEMETRY', icon: Activity, badge: '084', href: '/system-telemetry' },
      { id: 'api-keys', name: 'API KEYS', icon: Key, badge: '085', href: '/api-keys' },
      { id: 'webhooks-delivery', name: 'WEBHOOKS DELIVERY', icon: Radio, badge: '086', href: '/webhooks-delivery' },
      { id: 'tokenization-vault', name: 'TOKEN VAULT', icon: Lock, badge: '087', href: '/tokenization-vault' },
      { id: '3ds-authentication', name: '3DS AUTHENTICATION', icon: ShieldCheck, badge: '088', href: '/3ds-authentication' },
      { id: 'discrepancy-resolution', name: 'DISCREPANCY RESOLUTION', icon: AlertTriangle, badge: '089', href: '/discrepancy-resolution' },
      { id: 'partner-integrations', name: 'PARTNER CONNECTORS', icon: Plug, badge: '090', href: '/partner-integrations' },
      { id: 'tenant-isolation', name: 'TENANT ISOLATION', icon: Layers, badge: '091', href: '/tenant-isolation' },
      { id: 'kyc-verification', name: 'KYC VERIFICATION', icon: UserCheck, badge: '092', href: '/kyc-verification' },
      { id: 'sanctions-screening', name: 'SANCTIONS SCREENING', icon: Shield, badge: '093', href: '/sanctions-screening' },
      { id: 'disaster-recovery', name: 'DISASTER RECOVERY', icon: Server, badge: '094', href: '/disaster-recovery' },
      { id: 'rate-limiting', name: 'RATE LIMITING', icon: Activity, badge: '095', href: '/rate-limiting' },
      { id: 'vault-token-migration', name: 'TOKEN MIGRATION', icon: Lock, badge: '096', href: '/vault-token-migration' },
      { id: 'chargeback-auto-defense', name: 'AUTO-DEFENSE', icon: ShieldCheck, badge: '097', href: '/chargeback-auto-defense' },
      { id: 'payout-split-rules', name: 'PAYOUT SPLITS', icon: Percent, badge: '098', href: '/payout-split-rules' },
      { id: 'gateway-cascading-rules', name: 'GATEWAY CASCADING', icon: Network, badge: '099', href: '/gateway-cascading-rules' },
      { id: 'tax-nexus-monitoring', name: 'TAX NEXUS', icon: Scale, badge: '100', href: '/tax-nexus-monitoring' },
      { id: 'agent-spend-velocity', name: 'AGENT VELOCITY', icon: Zap, badge: '101', href: '/agent-spend-velocity' },
      { id: 'fraud-anomaly-signals', name: 'ANOMALY SIGNALS', icon: AlertTriangle, badge: '102', href: '/fraud-anomaly-signals' },
      { id: 'ledger-adjustment-logs', name: 'LEDGER ADJUSTMENTS', icon: FileCode, badge: '103', href: '/ledger-adjustment-logs' },
      { id: 'global-system-status', name: 'SYSTEM STATUS', icon: Server, badge: '104', href: '/global-system-status' },
      { id: 'payments', name: 'PAYMENTS', icon: CreditCard, badge: 'OPEX', href: '/payments' },
    ],
  },
  {
    group: 'SECURITY',
    items: [
      { id: 'agentguard', name: 'AGENTGUARD', icon: Shield, badge: 'POLICIES', href: '/agentguard' },
      { id: 'fraudguard', name: 'FRAUDGUARD', icon: Cpu, badge: 'AI RISK', href: '/fraudguard' },
      { id: 'risk-rules', name: 'RISK RULES', icon: Cpu, badge: '023', href: '/risk-rules' },
      { id: 'approvals', name: 'HUMAN APPROVALS', icon: ShieldCheck, badge: '024', href: '/approvals' },
      { id: 'audit-logs', name: 'AUDIT LOGS', icon: ShieldAlert, badge: '040', href: '/audit-logs' },
      { id: 'compliance', name: 'AML & COMPLIANCE', icon: FileCheck, badge: '042', href: '/compliance' },
    ],
  },
  {
    group: 'INTELLIGENCE',
    items: [
      { id: 'analytics', name: 'ANALYTICS', icon: BarChart3, href: '/analytics' },
    ],
  },
  {
    group: 'DEVELOPERS',
    items: [
      { id: 'developers', name: 'API / DEVELOPERS', icon: Code2, href: '/developers' },
      { id: 'system-health', name: 'SYSTEM HEALTH', icon: Activity, badge: '044', href: '/system-health' },
    ],
  },
  {
    group: 'SYSTEM',
    items: [
      { id: 'settings', name: 'SETTINGS', icon: Settings, href: '/settings' },
      { id: 'login', name: 'AUTH / LOGIN', icon: Lock, badge: 'SSO', href: '/login' },
    ],
  },
];

export function AgentPaySidebar({ activeTab, onTabChange }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <aside
      className={`bg-slate-950/95 border-r border-white/[0.08] flex flex-col justify-between transition-all duration-300 z-30 shrink-0 ${
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

        {/* Navigation Groups */}
        <div className="p-3 space-y-4 overflow-y-auto max-h-[calc(100vh-140px)]">
          {NAV_GROUPS.map((group) => (
            <div key={group.group} className="space-y-1">
              {!collapsed && (
                <div className="px-3 py-1 text-[9px] font-mono tracking-[0.2em] text-slate-500 uppercase font-semibold">
                  {group.group}
                </div>
              )}

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
          ))}
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
