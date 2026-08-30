# AGENTPAY — Availability Non-Functional Requirements

## 1. Overview

Availability requirements establish service uptime SLAs, operational measurement windows, excluded maintenance windows, and service availability monitoring methodologies.

---

## 2. Requirement Baseline

### NFR-AVAIL-001: Gateway API Service Availability SLA
* **NFR ID**: `NFR-AVAIL-001`
* **Title**: Gateway API Public & Agent Endpoint Availability SLA
* **Source FR**: `FR-AUTH-003`, `FR-INTENT-001`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Availability
* **Requirement**: The public API gateway and agent intent submission endpoints shall maintain a minimum service availability of 99.9%.
* **Rationale**: Payment gateways must remain continuously accessible to prevent agent payment rejections.
* **Metric & Target**:
  * Availability Target: $99.9\%$ Uptime per calendar month.
  * Maximum Allowed Unplanned Downtime: $\le 43.8\text{ minutes/month}$.
* **Measurement Window**: Monthly rolling 30-day window ($24 \times 7 \times 365$).
* **Measurement Method**: Automated synthetic HTTP ping checks every 30 seconds from dual geographical monitoring probes.
* **Excluded Events**: Scheduled maintenance windows announced $\ge 48\text{ hours}$ in advance (max 2 hours/month).
* **Acceptance Criteria**: Synthetic uptime checks achieve $\ge 99.9\%$ successful HTTP 200 responses over test period.
* **Dependencies**: Cloud load balancer availability.

---

### NFR-AVAIL-002: AGENTGUARD Policy Engine Availability SLA
* **NFR ID**: `NFR-AVAIL-002`
* **Title**: AGENTGUARD Policy Evaluation Engine Uptime SLA
* **Source FR**: `FR-AGD-001`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Availability
* **Requirement**: The AGENTGUARD policy engine shall maintain $99.95\%$ service availability.
* **Rationale**: Policy evaluation is on the critical payment path; engine unavailability blocks all agent commerce.
* **Metric & Target**: $99.95\%$ Uptime ($\le 21.9\text{ minutes/month}$ unplanned downtime).
* **Measurement Method**: Internal health check probe pinging `/health/agentguard` every 10 seconds.
* **Acceptance Criteria**: Health probe success rate $\ge 99.95\%$.
* **Dependencies**: Redis cluster availability.
