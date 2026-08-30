# AGENTPAY — 35: Automated Security Test Suite & Penetration Testing

## 1. Automated Security Testing Framework

* **SAST**: Semgrep security rules scanning for SQLi, XSS, and hardcoded secrets on every git push.
* **DAST**: OWASP ZAP automated REST API vulnerability scanner executing against staging environment.
* **BOLA / IDOR Automated Testing**: Integration test suite verifying that Tenant A cannot read/modify Tenant B's agent or transaction IDs.
