# AGENTPAY — 73: Whitelisted Deterministic Multi-Column Sort Architecture

## 1. Sorting Standard

* **Default Sort**: `created_at DESC, id DESC` (guarantees deterministic result ordering).
* **Whitelisted Fields**: Sort parameters are restricted to `created_at`, `amount`, `updated_at`. Un-whitelisted sort fields trigger HTTP 400 Bad Request.
