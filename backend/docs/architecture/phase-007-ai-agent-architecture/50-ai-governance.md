# AGENTPAY — 50: Model Deployment Quality Gate & Version Approvals

## 1. Governance Quality Gate

Deploying a new LLM prompt version or ML risk model binary requires:

1. **Automated Benchmark Pass**: Passing the 40 AI Red-Team simulation scenarios with $0$ bypasses.
2. **Precision Benchmark Pass**: $F_1 \ge 0.95$ on synthetic fraud dataset.
3. **Traceability Approval**: Mandatory registration of SHA-256 model checksum in Git model registry.
