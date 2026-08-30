# AGENTPAY — Resource Efficiency Non-Functional Requirements

## 1. Overview

Resource Efficiency requirements define container CPU and RAM allocation limits, database connection pooling constraints, and memory leak prevention rules.

---

## 2. Requirement Baseline

### NFR-RES-001: Container RAM & CPU Resource Boundaries
* **NFR ID**: `NFR-RES-001`
* **Title**: Container Memory & CPU Allocation Limits
* **Source FR**: All Functional Requirements
* **Priority**: P1 | **Target Horizon**: MVP TARGET
* **Category**: Resource Efficiency
* **Requirement**: Application API worker containers shall operate within a maximum RAM limit of 512 MB per container; FRAUDGUARD ML containers shall operate within 1.0 GB RAM.
* **Rationale**: Prevents un-throttled resource consumption and allows efficient local Docker Compose execution during hackathon demonstrations.
* **Metric & Target**: API Containers $\le 512\text{ MB RAM}$; ML Containers $\le 1.0\text{ GB RAM}$.
* **Measurement Method**: Docker Stats monitoring during stress test.
* **Acceptance Criteria**: Container RAM remains under allocation limits under full synthetic load.
* **Dependencies**: None.
