export interface OutboxEventRecord {
    outbox_event_id: string;
    tenant_id: string;
    aggregate_type: string;
    aggregate_id: string;
    event_type: string;
    payload: Record<string, unknown>;
    status: 'PENDING' | 'PUBLISHED' | 'FAILED';
}
//# sourceMappingURL=index.d.ts.map