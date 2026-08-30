# AGENTPAY — 57: Windows Local Development Compatibility (`pwsh` / `D:\`)

## 1. Windows Parity Standard

* Paths use forward slashes (`/`) in node scripts or `path.join()` / `path.resolve()`.
* CLI commands use cross-platform node utilities (`rimraf`, `tsx`, `cross-env`).
* Native PowerShell (`pwsh`) and CMD environments verified.
