import { listProviderStatus } from '../llm/providers';

export interface EnvReport {
  warnings: string[];
  providers: ReturnType<typeof listProviderStatus>;
  simulatedMode: boolean;
}

export function validateEnv(): EnvReport {
  const warnings: string[] = [];

  const port = process.env.PORT;
  if (port && (!Number.isInteger(Number(port)) || Number(port) < 1 || Number(port) > 65535)) {
    warnings.push(`PORT="${port}" is not a valid port number — falling back to 3001.`);
  }

  const origin = process.env.WEB_ORIGIN;
  if (origin) {
    try {
      const url = new URL(origin);
      if (url.protocol !== 'http:' && url.protocol !== 'https:') {
        warnings.push(`WEB_ORIGIN="${origin}" must be an http(s) URL — CORS may reject the web app.`);
      }
    } catch {
      warnings.push(`WEB_ORIGIN="${origin}" is not a valid URL — CORS may reject the web app.`);
    }
  }

  const pace = process.env.PIPELINE_PACE_MS;
  if (pace && (Number.isNaN(Number(pace)) || Number(pace) < 0)) {
    warnings.push(`PIPELINE_PACE_MS="${pace}" is not a valid number — pipeline pacing may misbehave.`);
  }

  const providers = listProviderStatus();
  const configured = providers.filter((p) => p.configured);
  const simulatedMode = configured.length === 0;

  if (simulatedMode) {
    warnings.push(
      'No LLM provider keys detected — running with simulated AI responses. Set OPENAI_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY, or OLLAMA_ENABLED=1 to enable real LLM calls.'
    );
  }

  return { warnings, providers, simulatedMode };
}
