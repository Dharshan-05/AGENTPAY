# AGENTPAY — 37: Model Confidence Thresholding & Disambiguation Queries

## 1. Disambiguation Protocol

If model confidence in intent understanding or entity extraction falls below 0.85, the agent MUST NOT generate a payment proposal. Instead, it issues a clarification query to the user (*"Did you mean flight option A for ₹12,500 or option B for ₹14,200?"*).
