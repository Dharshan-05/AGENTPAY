# MONO-ADR-024: Open-Source Dependency Governance & License Compliance

## 1. Context & Problem Statement
Preventing license contamination or vulnerable zero-day third-party package dependencies from entering production builds.

## 2. Decision
Enforce dependency license checks (allowing MIT, Apache-2.0, BSD) and automate `pnpm audit` checks in CI pipelines.

## 3. Consequences & Trade-Offs
* **Benefits**: Protects against legal license violations and known third-party vulnerabilities.
* **Trade-Offs**: Requires updating or replacing packages flagged by dependency audits.
