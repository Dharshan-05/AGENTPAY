# SEC-ADR-015: Software Supply Chain Security & SBOM Generation

## Context & Problem Statement
Third-party dependencies (npm, PyPI) introduce supply-chain vulnerabilities and malicious package risks.

## Threat Analysis
A compromised npm package dependency could exfiltrate internal environment variables or modify payment payloads.

## Decision
Enforce lockfile SHA pinning, generate Syft SBOM artifacts, and execute Trivy container scans. Fail CI/CD builds on high/critical CVEs.

## Consequences & Trade-Offs
* **Benefits**: Protects build pipeline against software supply chain attacks.
* **Trade-Offs**: Requires periodic updating and auditing of third-party dependencies.
