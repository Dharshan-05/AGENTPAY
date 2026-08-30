# AGENTPAY — 85: Automated API Security & Injection Penetration Suite

## 1. Security Testing Suite

* **Mass Assignment Test**: Submits forbidden `status="SUCCESS"` in request JSON body; verifies key strip / HTTP 400 rejection.
* **Tenant Isolation Test**: Requests foreign tenant resource ID; verifies HTTP 404 Not Found response.
* **SQL Injection Test**: Passes SQL injection payloads (`' OR 1=1 --`) in path parameters; verifies 100% rejection.
