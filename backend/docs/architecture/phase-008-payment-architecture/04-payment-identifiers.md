# AGENTPAY — 04: 18 Distinct GUID Identifiers & Provider Mappings

## 1. Primary Identifier Taxonomy

To maintain domain clarity and prevent ID collision, AGENTPAY enforces 18 distinct GUID identifier types:

1. `tenant_id`: Multi-tenant organization GUID (`tenant_7f8a9b0c`).
2. `user_id`: Human account owner GUID (`usr_91a0b2c3`).
3. `agent_id`: Autonomous AI agent GUID (`agt_8f9b2c3a`).
4. `merchant_id`: Commercial merchant GUID (`mch_12345678`).
5. `order_id`: Internal purchase order GUID (`ord_3f2a1b0c`).
6. `payment_intent_id`: Payment intent proposal GUID (`intent_7f8a9b0c`).
7. `payment_authorization_id`: Authorization context token GUID (`auth_9f8a7b6c`).
8. `payment_id`: Internal payment settlement GUID (`pay_1a2b3c4d`).
9. `payment_attempt_id`: Payment provider attempt GUID (`att_5e6f7g8h`).
10. `provider_payment_id`: External Razorpay payment ID (`pay_K123456789`).
11. `provider_order_id`: External Razorpay order ID (`order_K987654321`).
12. `refund_id`: Internal refund request GUID (`ref_11223344`).
13. `webhook_event_id`: Razorpay webhook event ID (`evt_55667788`).
14. `reconciliation_id`: Reconciliation job GUID (`rec_99001122`).
15. `ledger_entry_id`: Double-entry accounting line GUID (`led_33445566`).
16. `idempotency_key`: Client-provided deduplication UUID (`idemp_uuid_v4`).
17. `transaction_id`: End-to-end trace correlation UUID (`tx_7f8a9b0c`).
18. `decision_id`: AGENTGUARD authorization decision GUID (`dec_9f8a7b6c`).
