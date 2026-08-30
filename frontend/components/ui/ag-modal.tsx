'use client';

import React from 'react';
import { X } from 'lucide-react';

interface AGModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function AGModal({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  footer,
}: AGModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md transition-opacity"
        onClick={onClose}
      />

      {/* Modal Card */}
      <div className="relative w-full max-w-2xl bg-slate-900 border border-white/[0.1] rounded-2xl shadow-2xl overflow-hidden z-10 font-mono text-xs">
        {/* Header */}
        <div className="p-6 border-b border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider block">
              {subtitle || 'AGENTPAY MODAL'}
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

        {/* Body */}
        <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">{children}</div>

        {/* Footer */}
        {footer && (
          <div className="p-4 border-t border-white/[0.08] bg-slate-950/60 flex justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
