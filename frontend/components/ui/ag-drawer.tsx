'use client';

import React from 'react';
import { X } from 'lucide-react';

interface AGDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function AGDrawer({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  footer,
}: AGDrawerProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Overlay Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md transition-opacity"
        onClick={onClose}
      />

      {/* Drawer Container */}
      <div className="relative w-full max-w-lg bg-slate-900 border-l border-white/[0.1] shadow-2xl flex flex-col h-full z-10 font-mono text-xs">
        {/* Header */}
        <div className="p-6 border-b border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider block">
              {subtitle || 'INSPECTION DRAWER'}
            </span>
            <h3 className="font-display text-lg font-bold text-slate-100 mt-0.5">
              {title}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 p-6 overflow-y-auto space-y-6">{children}</div>

        {/* Footer */}
        {footer && (
          <div className="p-6 border-t border-white/[0.08] bg-slate-950/60">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
