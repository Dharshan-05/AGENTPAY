# AGENTPAY — Open Decisions Registry

## 1. Overview

This document tracks technical open decisions inherited from Phase 001 and Phase 002. Each decision outlines the original question, context, available options, recommended path, architectural impact, and resolution status.

---

## 2. Decision Registry

### Decision 001: Database Engine Selection for Phase 003+
* **Decision ID**: `DEC-001`
* **Original Question**: Should AGENTPAY utilize PostgreSQL (with pgvector / JSONB) or SQLite as the primary database engine for Phase 003+?
* **Context**: PostgreSQL offers production-grade concurrency, row-level locking, JSONB index support, and vector search. SQLite offers zero-dependency local setup ideal for fast hackathon demo deployment.
* **Options Considered**:
  1. **Option A (Recommended)**: PostgreSQL (via Docker Compose) with Prisma / Drizzle ORM.
  2. **Option B**: SQLite for local zero-config testing.
* **Recommended Option**: **Option A (PostgreSQL via Docker)**.
* **Reasoning**: Concurrent agent intent execution, atomic daily limit updates, and append-only audit trail block hashing require robust relational locking and JSONB query capabilities present in PostgreSQL.
* **Architectural Impact**: Requires Docker Compose file providing PostgreSQL container for local development.
* **Status**: RESOLVED (Adopted PostgreSQL via Docker for Phase 003+).

---

### Decision 002: UI Component Library for Web Dashboard
* **Decision ID**: `DEC-002`
* **Original Question**: What UI component library and styling framework should be selected for the frontend Web Dashboard and Approval Center?
* **Context**: The hackathon demo requires a polished, modern, highly responsive FinTech dashboard displaying real-time risk scores, XAI traces, and approval workflows.
* **Options Considered**:
  1. **Option A (Recommended)**: Next.js (React) + Tailwind CSS + Shadcn UI + Lucide Icons.
  2. **Option B**: Custom CSS framework built from scratch.
* **Recommended Option**: **Option A (Next.js + Tailwind CSS + Shadcn UI)**.
* **Reasoning**: Shadcn UI provides accessible, beautifully styled, customizable components (cards, dialogs, badges, tables, alerts) allowing rapid construction of the Approval Center and Security Console.
* **Architectural Impact**: Establishes standard React component structure under `apps/web`.
* **Status**: RESOLVED (Adopted Next.js + Tailwind CSS + Shadcn UI).
