# AGENTPAY — 56: Developer Step-by-Step Onboarding Guide

## 1. Prerequisites Checklist

* Node.js `v20.11.0 LTS`
* PNPM `v9.1.0` (`npm i -g pnpm@9`)
* Docker Desktop 4.x (with Compose v2)
* Python `3.11+`

---

## 2. Onboarding Workflow

1. Clone repository to local machine (`git clone ...`).
2. Run `pnpm install` in root directory.
3. Copy `.env.example` to `.env.local`.
4. Run `docker-compose up -d` to launch Postgres and Redis.
5. Run `pnpm db:migrate` followed by `pnpm db:seed`.
6. Run `pnpm dev` to start all applications.
