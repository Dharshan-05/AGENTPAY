'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { AGButton } from '@/components/ui/ag-button';
import { CreditCard, RefreshCw, Download } from 'lucide-react';

interface SourceHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
}

export function SourceHeader({ onRefresh, onExport }: SourceHeaderProps) {
  return (
    <PageHeader
      eyebrow="PAYMENT METHOD + INSTRUMENT CONTROL PLANE"
      title="PAYMENT METHOD SOURCE"
      highlightTitle="EXPLORER"
      description="Reverse-engineered payment instrument architecture, card & bank account tokenization, multi-connector processor routing, Zero-Trust PCI vaulting, and autonomous agent payment governance."
      icon={CreditCard}
      statusBadge="● PAYMENT METHOD ENGINE RESEARCH ONLINE"
      actions={
        <div className="flex items-center gap-2 font-mono">
          <AGButton variant="ghost" size="sm" onClick={onRefresh}>
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH
          </AGButton>
          <AGButton variant="secondary" size="sm" onClick={onExport}>
            <Download className="w-3.5 h-3.5 mr-1.5" /> EXPORT RESEARCH LEDGER
          </AGButton>
        </div>
      }
    />
  );
}
