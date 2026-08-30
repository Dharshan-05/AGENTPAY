'use client';

import { AGBadge, AGBadgeStatus } from '@/components/ui/ag-badge';
import { ApiKeyStatus } from './developers-types';

interface ApiKeyStatusBadgeProps {
  status: ApiKeyStatus;
}

export function ApiKeyStatusBadge({ status }: ApiKeyStatusBadgeProps) {
  let mappedStatus: AGBadgeStatus = 'ACTIVE';

  switch (status) {
    case 'ACTIVE':
      mappedStatus = 'APPROVED';
      break;
    case 'REVOKED':
      mappedStatus = 'BLOCKED';
      break;
    case 'ROTATION_REQUIRED':
      mappedStatus = 'REVIEW';
      break;
    case 'SANDBOX':
      mappedStatus = 'PENDING';
      break;
    default:
      mappedStatus = 'ACTIVE';
  }

  return <AGBadge status={mappedStatus} label={`● ${status}`} />;
}
