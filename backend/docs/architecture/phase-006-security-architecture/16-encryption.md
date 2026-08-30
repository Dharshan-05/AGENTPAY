# AGENTPAY — 16: Encryption Architecture (TLS 1.3, AES-256-GCM)

## 1. Encryption Standards

* **In Transit**: TLS 1.3 mandated across external and internal microservice communications. Cipher suites restricted to AES-256-GCM and CHACHA20-POLY1305.
* **At Rest**: PostgreSQL database storage and Redis persistence encrypted via AES-256-GCM disk volume encryption.
* **Field-Level**: Sensitive user tokens encrypted at application layer using AES-256-GCM with unique Initialization Vectors (IV).
