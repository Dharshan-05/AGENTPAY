# AGENTPAY — 22: `@agentpay/api-contracts` Shared Schema Foundation

## 1. Shared Zod Contracts

Both `apps/api` and `apps/web` import `@agentpay/api-contracts` to validate request parameters and infer TypeScript interfaces:

```typescript
export const CreatePaymentIntentRequestSchema = z.object({
  order_id: z.string().startsWith('ord_'),
  merchant_id: z.string().startsWith('mch_'),
  amount: z.number().int().positive(),
  currency: z.enum(['INR', 'USD', 'EUR']).default('INR')
});
```
