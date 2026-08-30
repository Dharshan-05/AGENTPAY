import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { loadEnv } from '@agentpay/config';
import { logger } from '@agentpay/observability';

const env = loadEnv();
const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'OK', service: 'agentpay-api', timestamp: new Date().toISOString() });
});

if (process.env.NODE_ENV !== 'test') {
  app.listen(env.PORT, () => {
    logger.info(`AGENTPAY Core API Gateway running on port ${env.PORT}`);
  });
}

export default app;
