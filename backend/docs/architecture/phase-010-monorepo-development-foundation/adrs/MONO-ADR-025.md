# MONO-ADR-025: Cross-Platform Windows & Linux Developer Compatibility

## 1. Context & Problem Statement
Ensuring that repository build scripts, paths, and CLI commands function seamlessly on Windows local environments (`D:\PROJECT\ANGENT PAY`) and Linux CI runners.

## 2. Decision
Ban bash-only shell syntax (`sed`, `awk`, `grep`) in `package.json` scripts; utilize cross-platform Node.js tools (`tsx`, `shx`, `rimraf`, `cross-env`).

## 3. Consequences & Trade-Offs
* **Benefits**: 100% developer parity across Windows (PowerShell/CMD) and Linux environments.
* **Trade-Offs**: Build scripts must be written as Node.js or cross-platform NPM commands.
