# AGENTPAY — 07: Abstract `IPaymentProvider` & Adapter Pattern Interface

## 1. Abstract Adapter Interface

To decouple AGENTPAY core domain logic from specific payment providers, all gateway integrations implement an abstract TypeScript interface:

```typescript
export interface IPaymentProvider {
  provider_id: string; // "razorpay"
  
  createOrder(intent: PaymentIntent): Promise<ProviderOrderResult>;
  executePayment(authorization: PaymentAuthorizationContext): Promise<ProviderSettlementResult>;
  getPayment(providerPaymentId: string): Promise<ProviderPaymentDetails>;
  refundPayment(refund: RefundRequest): Promise<ProviderRefundResult>;
  verifyWebhookSignature(rawBody: string, signature: string, secret: string): boolean;
  reconcileSettlements(startDate: Date, endDate: Date): Promise<ProviderReconciliationBatch>;
}
```
