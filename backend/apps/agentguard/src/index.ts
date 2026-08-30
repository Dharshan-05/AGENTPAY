import express from 'express';

const app = express();
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'OK', service: 'agentguard-control-plane' });
});

export default app;
