import { PayoutScheduleRecord } from './payout-schedule-types';
export const MOCK_PAYOUT_SCHEDULES: PayoutScheduleRecord[] = [
  { id: 'ps1', scheduleId: 'PSCH-AGP-001', accountRef: 'MER-AGP-001 (Acme Corp)', cadence: 'DAILY_AUTOMATIC', rollingReservePercent: '5.0%', nextPayoutDate: '2026-08-31', payoutMethod: 'ACH_DIRECT_DEPOSIT', status: 'ACTIVE' },
  { id: 'ps2', scheduleId: 'PSCH-AGP-002', accountRef: 'MER-AGP-002 (Global AI)', cadence: 'WEEKLY_MONDAY', rollingReservePercent: '10.0%', nextPayoutDate: '2026-09-07', payoutMethod: 'SEPA_INSTANT', status: 'ACTIVE' },
];
