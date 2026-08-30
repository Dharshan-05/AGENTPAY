# AGENTPAY — 47: Developer Quick-Start Reference

## 1. Quick-Start Workflow

```bash
# 1. Clone & Install
pnpm install

# 2. Setup Environment Variables
cp .env.example .env.local

# 3. Start Local Postgres & Redis Containers
docker-compose up -d postgres redis

# 4. Run Migrations & Seed Data
pnpm db:migrate
pnpm db:seed

# 5. Start Development Applications
pnpm dev
```
