import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/server.ts'],
  format: ['esm'],
  target: 'node18',
  outDir: 'dist',
  clean: true,
  sourcemap: true,
  splitting: false,
  minify: false,
  dts: false,
  external: ['@prisma/client'],
  noExternal: [
    '@fastify/*',
    '@sentry/*',
    'bullmq',
    'ioredis',
    'jsonwebtoken',
    'mongodb',
    'openai',
    'razorpay',
    'resend',
    'socket.io',
    'tiktoken',
  ],
  banner: {
    js: 'import { createRequire } from "module"; import { fileURLToPath } from "url"; import { dirname, resolve } from "path"; const require = createRequire(import.meta.url); const __filename = fileURLToPath(import.meta.url); const __dirname = dirname(__filename);',
  },
})