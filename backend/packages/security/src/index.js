"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.hashSHA256 = hashSHA256;
const crypto_1 = __importDefault(require("crypto"));
function hashSHA256(data) {
    return crypto_1.default.createHash('sha256').update(data).digest('hex');
}
//# sourceMappingURL=index.js.map