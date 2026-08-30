"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EnvSchema = void 0;
exports.loadEnv = loadEnv;
const zod_1 = require("zod");
exports.EnvSchema = zod_1.z.object({
    NODE_ENV: zod_1.z.enum(['development', 'test', 'staging', 'production']).default('development'),
    PORT: zod_1.z.coerce.number().default(4000),
    DATABASE_URL: zod_1.z.string().default('postgresql://postgres:postgres_dev_pass@localhost:5432/agentpay_dev'),
    REDIS_URL: zod_1.z.string().default('redis://localhost:6379')
});
function loadEnv() {
    return exports.EnvSchema.parse(process.env);
}
//# sourceMappingURL=index.js.map