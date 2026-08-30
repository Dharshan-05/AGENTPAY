/**
 * AGENTPAY MASTER DESIGN SYSTEM TOKENS
 * Single Source of Truth for Visual Language, Status Colors, Typography & Surfaces.
 */

export const AG_TOKENS = {
  colors: {
    background: '#020617', // Obsidian Black
    surface: '#090D16', // Deep Slate Surface
    surfaceElevated: '#0F172A', // Elevated Panel Slate
    surfaceHover: '#1E293B', // Hover Accent Slate
    border: 'rgba(255, 255, 255, 0.08)', // Subtle Hairline Border
    borderStrong: 'rgba(255, 255, 255, 0.15)', // Active/Selected Border
    
    // Brand Accent
    brand: '#10B981', // Trust Emerald
    brandGlow: 'rgba(16, 185, 129, 0.2)',
    
    // Status Accents
    success: '#10B981', // Trust Emerald
    warning: '#F59E0B', // Shield Amber
    danger: '#EF4444', // Alert Crimson
    info: '#3B82F6', // Sovereign Blue
    ai: '#8B5CF6', // Neural Violet
    
    // Text Hierarchy
    textPrimary: '#F8FAFC',
    textSecondary: '#94A3B8',
    textMuted: '#64748B',
  },
  typography: {
    fontDisplay: 'Space Grotesk, sans-serif',
    fontBody: 'Inter, sans-serif',
    fontMono: 'JetBrains Mono, monospace',
  },
  statusMap: {
    ACTIVE: { label: 'ACTIVE', bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
    AUTHORIZED: { label: 'AUTHORIZED', bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
    APPROVED: { label: 'APPROVED', bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
    LIVE: { label: 'LIVE', bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
    POLICY_SECURE: { label: 'POLICY SECURE', bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
    LOW_RISK: { label: 'LOW RISK', bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
    
    PENDING: { label: 'PENDING', bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30', dot: 'bg-amber-400' },
    PENDING_APPROVAL: { label: 'PENDING APPROVAL', bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30', dot: 'bg-amber-400' },
    REVIEW: { label: 'REVIEW', bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30', dot: 'bg-amber-400' },
    
    BLOCKED: { label: 'BLOCKED', bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30', dot: 'bg-red-400' },
    DENIED: { label: 'DENIED', bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30', dot: 'bg-red-400' },
    HIGH_RISK: { label: 'HIGH RISK', bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30', dot: 'bg-red-400' },
    CRITICAL: { label: 'CRITICAL', bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/40', dot: 'bg-red-500' },
  },
};
