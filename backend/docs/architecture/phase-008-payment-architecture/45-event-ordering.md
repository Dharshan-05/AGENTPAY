# AGENTPAY — 45: Sequence Numbers & Out-of-Order Event Handling

## 1. Event Sequence Rules

Every domain event carries an incremental `sequence_number` scoped to the `payment_intent_id`. If an event arrives out of order (e.g. `PaymentSucceeded` before `PaymentProcessing`), the consumer checks sequence state, buffering out-of-order events in Redis until missing antecedents process.
