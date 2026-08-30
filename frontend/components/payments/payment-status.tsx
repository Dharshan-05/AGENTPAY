'use client';

import { AGBadge, AGBadgeStatus } from '@/components/ui/ag-badge';
import { PaymentStatusType } from './types';

interface PaymentStatusBadgeProps {
  status: PaymentStatusType;
}

export function PaymentStatusBadge({ status }: PaymentStatusBadgeProps) {
  let mappedStatus: AGBadgeStatus = 'ACTIVE';

  switch (status) {
    case 'PAID':
    case 'SETTLED':
    case 'AUTHORIZED':
    case 'CAPTURED':
      mappedStatus = 'APPROVED';
      break;
    case 'PENDING':
    case 'PROCESSING':
      mappedStatus = 'PENDING';
      break;
    case 'FAILED':
    case 'DECLINED':
    case 'BLOCKED':
      mappedStatus = 'BLOCKED';
      break;
    case 'REFUNDED':
    case 'REVIEW':
      mappedStatus = 'REVIEW';
      break;
    default:
      mappedStatus = 'ACTIVE';
  }

  return <AGBadge status={mappedStatus} label={`● ${status}`} />;
}
