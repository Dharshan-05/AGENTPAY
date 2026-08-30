'use client';
export type RecurringTabType = 'SCHEDULE' | 'EXECUTIONS' | 'DUNNING_RETRY' | 'SUCCESSFUL' | 'FAILED' | 'SMART_ROUTING' | 'AUDIT';
export interface RecurringPaymentRecord {
  id: string;
  recurringId: string;
  mandateRef: string;
  agentId: string;
  amount: string;
  nextExecutionDate: string;
  retryAttempt: number;
  status: 'SCHEDULED' | 'EXECUTING' | 'FAILED_DUNNING';
}
