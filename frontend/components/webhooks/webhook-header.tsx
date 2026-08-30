'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { AGButton } from '@/components/ui/ag-button';
import { Radio, RefreshCw, Download, Plus } from 'lucide-react';

interface WebhookHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
  onRegister: () => void;
}

export function WebhookHeader({ onRefresh, onExport, onRegister }: WebhookHeaderProps) {
  return (
    <PageHeader
      eyebrow="WEBHOOK + EVENT DELIVERY CONTROL PLANE"
      title="WEBHOOK"
      highlightTitle="OPERATIONS"
      description="Zero-trust webhook delivery engine, real-time event routing, HMAC-SHA256 signature security, exponential backoff retries, and tamper-evident audit trails."
      icon={Radio}
      statusBadge="● DELIVERY ENGINE ONLINE"
      actions={
        <div className="flex items-center gap-2 font-mono">
          <AGButton variant="ghost" size="sm" onClick={onRefresh}>
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH
          </AGButton>
          <AGButton variant="secondary" size="sm" onClick={onExport}>
            <Download className="w-3.5 h-3.5 mr-1.5" /> EXPORT LEDGER
          </AGButton>
          <AGButton variant="primary" size="sm" onClick={onRegister}>
            <Plus className="w-3.5 h-3.5 mr-1.5" /> REGISTER ENDPOINT
          </AGButton>
        </div>
      }
    />
  );
}
