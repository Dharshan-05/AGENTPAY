import { z } from 'zod';
export declare const EnvSchema: any;
export type Env = z.infer<typeof EnvSchema>;
export declare function loadEnv(): Env;
//# sourceMappingURL=index.d.ts.map