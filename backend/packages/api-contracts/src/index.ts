import { z } from 'zod';

export const CreatePaymentIntentSchema = z.object({
  order_id: z.string(),
  merchant_id: z.string(),
  amount: z.number().int().positive(),
  currency: z.enum(['INR', 'USD', 'EUR']).default('INR')
});

export type CreatePaymentIntentInput = z.infer<typeof CreatePaymentIntentSchema>;
