# AGENTPAY — 28: CI/CD Pipeline SAST/DAST & Container Scanning Gates

## 1. Security Quality Gate Pipeline

```
[ COMMIT ] ──> Secret Scan (TruffleHog) ──> SAST (Semgrep) ──> Dependency Audit ──> Container Scan (Trivy) ──> Security Gate (PASS/FAIL) ──> DEPLOY
```

Any build exhibiting hardcoded secrets, high-severity SAST vulnerabilities, or unpatched container OS CVEs fails the pipeline.
