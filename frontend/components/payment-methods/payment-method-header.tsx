'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { AGButton } from '@/components/ui/ag-button';
import { CreditCard, RefreshCw, Download, Plus } from 'lucide-react';

interface PaymentMethodHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
  onAddMethod: () => void;
}

export function PaymentMethodHeader({ onRefresh, onExport, onAddMethod }: PaymentMethodHeaderProps) {
  return (
    <PageHeader
      eyebrow="PAYMENT METHOD + INSTRUMENT CONTROL PLANE"
      title="PAYMENT METHOD"
      highlightTitle="OPERATIONS"
      description="Autonomous agent payment instrument governance, network tokenization vault, multi-connector processor routing, Zero-Trust PCI compliance, and real-time FraudGuard risk control."
      icon={CreditCard}
      statusBadge="● METHOD ENGINE ONLINE"
      actions={
        <div className="flex items-center gap-2 font-mono">
          <AGButton variant="ghost" size="sm" onClick={onRefresh}>
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH
          </AGButton>
          <AGButton variant="secondary" size="sm" onClick={onExport}>
            <Download className="w-3.5 h-3.5 mr-1.5" /> EXPORT LEDGER
          </AGButton>
          <AGButton variant="primary" size="sm" onClick={onAddMethod}>
            <Plus className="w-3.5 h-3.5 mr-1.5" /> ADD PAYMENT METHOD
          </AGButton>
        </div>
      }
    />
  );
}
