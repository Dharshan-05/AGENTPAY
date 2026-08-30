# AGENTPAY — 43: Database Security & Connection Role Privilege Restrictions

## 1. Database Role Privilege Matrix

| Role Name | Connect | SELECT | INSERT / UPDATE | DELETE | DDL Schema |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `agentpay_app` | YES | YES | YES | NO (Financial Tables) | NO |
| `agentpay_migrator`| YES | YES | YES | YES | YES |
| `agentpay_analytics`| YES | YES | NO | NO | NO |
| `postgres` (Super) | Denied from App Network Subnet | YES | YES | YES | YES |

Connections mandate TLS v1.3 with certificate validation (`sslmode=verify-full`).
