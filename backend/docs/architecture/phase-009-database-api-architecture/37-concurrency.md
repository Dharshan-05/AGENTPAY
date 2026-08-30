# AGENTPAY — 37: Pessimistic DB Row Locking (`SELECT FOR UPDATE`) & Optimistic Locking

## 1. Hybrid Concurrency Architecture

* **Pessimistic Row Locking (`SELECT FOR UPDATE`)**: Used when executing payment settlements, ensuring that only a single worker thread holds the row lock during provider API dispatch.
* **Optimistic Locking (`version` column)**: Used for state updates that do not require external HTTP network calls.
