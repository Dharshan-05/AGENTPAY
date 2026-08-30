# AGENTPAY — 15: Database Security, Least Privilege & Parameterization

## 1. Database Least Privilege Roles

1. `app_runtime_role`: Granted `SELECT`, `INSERT`, `UPDATE` on application tables. Denied schema alterations (`ALTER`, `DROP`). Denied `UPDATE`/`DELETE` on `audit_logs`.
2. `audit_archiver_role`: Granted `INSERT` only on `audit_logs`.
3. `migration_role`: Used exclusively during automated CI/CD migrations.

---

## 2. SQL Injection Defenses

100% of database queries use parameterized SQL prepared statements via Prisma / Drizzle ORM. Raw SQL string concatenation is strictly forbidden.
