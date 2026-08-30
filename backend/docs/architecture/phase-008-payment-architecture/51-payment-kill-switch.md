# AGENTPAY — 51: Multi-Tier Emergency Payment Kill Switch Architecture

## 1. Emergency Kill Switch Tiers

```
+-----------------------------------------------------------------------+
|                    MULTI-TIER EMERGENCY KILL SWITCHES                 |
+-----------------------------------------------------------------------+
|  1. Global Kill Switch  : Freezes all platform payment processing.      |
|  2. Tenant Kill Switch  : Freezes all payments for specific user.      |
|  3. Agent Kill Switch   : Freezes payments for specific target agent.  |
|  4. Merchant Kill Switch: Blocks payments to specific merchant domain.|
+-----------------------------------------------------------------------+
```

Kill switches propagate in $< 100\text{ ms}$ via Redis flags, executing fail-closed controls on incoming intents.
