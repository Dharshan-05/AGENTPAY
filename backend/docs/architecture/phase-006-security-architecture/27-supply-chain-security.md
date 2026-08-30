# AGENTPAY — 27: Dependency SBOM, Lockfile & Package Auditing

## 1. Supply Chain Controls

* **Software Bill of Materials (SBOM)**: Generated using Syft/CycloneDX on every build.
* **Pinning & Lockfiles**: All npm and Python pip packages are pinned to exact commit SHA / lockfile hashes (`package-lock.json`, `requirements.txt`).
* **Dependency Vulnerability Scanning**: `npm audit` and `pip-audit` execute on every PR. Builds containing critical vulnerabilities fail automatically.
