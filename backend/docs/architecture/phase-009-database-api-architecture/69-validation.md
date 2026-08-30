# AGENTPAY — 69: Strict Input Request Validation (Zod / JSON Schema)

## 1. Zod Ingress Validation Pipeline

All request body payloads undergo strict runtime schema validation before reaching application controllers:

```typescript
export const PaymentIntentSchema = z.object({
  order_id: z.string().startsWith('ord_'),
  merchant_id: z.string().startsWith('mch_'),
  amount: z.number().int().positive(),
  currency: z.enum(['INR', 'USD', 'EUR'])
}).strict(); // Strip/reject unknown fields
```
