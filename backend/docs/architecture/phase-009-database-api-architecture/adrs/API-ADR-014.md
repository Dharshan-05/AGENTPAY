# API-ADR-014: Security Response Header Enforcement at API Gateway Edge

## 1. Context & Problem Statement
Protecting API clients against clickjacking, MIME-sniffing, and cross-site scripting attacks.

## 2. Decision
Enforce strict security headers (`HSTS`, `X-Content-Type-Options`, `X-Frame-Options`) on 100% of API HTTP responses.

## 3. Consequences & Trade-Offs
* **Benefits**: Hardens browser API clients against common web vulnerabilities.
* **Trade-Offs**: Requires configuring header injection at API Gateway ingress.
