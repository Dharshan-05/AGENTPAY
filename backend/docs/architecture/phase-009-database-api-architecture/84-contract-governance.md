# AGENTPAY — 84: API Contract Governance & Deprecation Policy

## 1. Contract Governance Rules

* **Automated CI Validation**: `spectral lint openapi.yaml` checks all API spec changes in CI pipelines.
* **Breaking Change Gate**: Pull requests introducing breaking contract changes (field deletions, path renaming) fail automated CI checks unless versioned under `/api/v2/`.
