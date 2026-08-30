# AGENTPAY — 09: Node.js Engine Pinning (`.nvmrc` & packageManager)

## 1. Engine Versions

* **Node.js**: `v20.11.0 LTS` (Enforced via `.nvmrc`).
* **Package Manager**: `pnpm@9.1.0` (Enforced via root `package.json` `"packageManager"` field).
* **Cross-Platform Scripting**: Shell commands use Node.js binaries (`tsx`, `shx`, `rimraf`) for Windows/Linux parity.
