"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreatePaymentIntentSchema = void 0;
const zod_1 = require("zod");
exports.CreatePaymentIntentSchema = zod_1.z.object({
    order_id: zod_1.z.string(),
    merchant_id: zod_1.z.string(),
    amount: zod_1.z.number().int().positive(),
    currency: zod_1.z.enum(['INR', 'USD', 'EUR']).default('INR')
});
//# sourceMappingURL=index.js.map