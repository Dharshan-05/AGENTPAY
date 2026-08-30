"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const config_1 = require("@agentpay/config");
const observability_1 = require("@agentpay/observability");
const env = (0, config_1.loadEnv)();
const app = (0, express_1.default)();
app.use((0, helmet_1.default)());
app.use((0, cors_1.default)());
app.use(express_1.default.json());
app.get('/health', (_req, res) => {
    res.json({ status: 'OK', service: 'agentpay-api', timestamp: new Date().toISOString() });
});
if (process.env.NODE_ENV !== 'test') {
    app.listen(env.PORT, () => {
        observability_1.logger.info(`AGENTPAY Core API Gateway running on port ${env.PORT}`);
    });
}
exports.default = app;
//# sourceMappingURL=index.js.map