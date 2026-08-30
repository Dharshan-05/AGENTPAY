'use client';
export type PayoutSchedulesTabType = 'SCHEDULES' | 'RESERVE_HOLDS' | 'PAYOUT_METHODS' | 'AUTOMATED_TRIGGERS' | 'AUDIT';
export interface PayoutScheduleRecord {
  id: string;
  scheduleId: string;
  accountRef: string;
  cadence: 'DAILY_AUTOMATIC' | 'WEEKLY_MONDAY' | 'MONTHLY_1ST';
  rollingReservePercent: string;
  nextPayoutDate: string;
  payoutMethod: string;
  status: 'ACTIVE' | 'PAUSED';
}
