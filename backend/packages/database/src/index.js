"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createDatabasePool = createDatabasePool;
const pg_1 = require("pg");
function createDatabasePool(connectionString) {
    return new pg_1.Pool({ connectionString });
}
//# sourceMappingURL=index.js.map