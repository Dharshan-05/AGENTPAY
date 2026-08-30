# AGENTPAY — 49: Container Security Hardening (Non-Root Users & Minimal Images)

## 1. Container Security Hardening

* **Non-Root Execution**: Dockerfiles run application processes under non-privileged user `node` (`USER node`).
* **Minimal Base Images**: Production multi-stage Docker builds use `node:20-alpine` and `python:3.11-slim`.
* **Zero Secret Baking**: Production image builds strictly exclude `.env` files.
