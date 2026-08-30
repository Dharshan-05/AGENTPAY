# AGENTPAY — 42: Database RPO (< 1s) & RTO (< 15m) Point-in-Time Recovery

## 1. Recovery Targets

* **Recovery Point Objective (RPO)**: $< 1\text{ second}$ (Synchronous WAL streaming replication to standby node).
* **Recovery Time Objective (RTO)**: $< 15\text{ minutes}$ (Automated Patroni / AWS RDS multi-AZ failover).
* **Point-In-Time Recovery (PITR)**: Enables restoring financial state to any precise microsecond timestamp within past 30 days.
