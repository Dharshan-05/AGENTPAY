import type { AgentResult, AgentStatusType, AgentTraceEntry, InspectorOutput } from "../lib/types";
import { AgentStatus,  } from "../lib/types";

export abstract class BaseAgent<TInput, TOutput> {
  readonly name: string;
  readonly version: string;
  readonly responsibility: string;
  readonly startTime: number;
  status: AgentStatusType = AgentStatus.PENDING;
  confidence = 0;
  executionTimeMs = 0;
  error: string | undefined;

  constructor(name: string, responsibility: string, version = '1.0.0') {
    this.name = name;
    this.responsibility = responsibility;
    this.version = version;
    this.startTime = Date.now();
  }

  async run(input: TInput): Promise<AgentResult<TOutput>> {
    this.status = AgentStatus.RUNNING;
    const started = performance.now();
    try {
      const output = await this.execute(input);
      this.executionTimeMs = Math.round(performance.now() - started);
      this.status = AgentStatus.COMPLETED;
      this.confidence = this.calculateConfidence(output);
      return {
        status: this.status,
        confidence: this.confidence,
        executionTimeMs: this.executionTimeMs,
        output,
      };
    } catch (err) {
      this.executionTimeMs = Math.round(performance.now() - started);
      this.status = AgentStatus.FAILED;
      this.error = err instanceof Error ? err.message : String(err);
      return {
        status: this.status,
        confidence: 0,
        executionTimeMs: this.executionTimeMs,
        output: null as TOutput,
        error: this.error,
      };
    }
  }

  protected abstract execute(input: TInput): Promise<TOutput>;

  protected abstract calculateConfidence(output: TOutput): number;

  toTrace(): AgentTraceEntry {
    return {
      agent: this.name,
      status: this.status,
      confidence: this.confidence,
      executionTimeMs: this.executionTimeMs,
      startedAt: new Date(this.startTime).toISOString(),
      error: this.error,
    };
  }
}

export function mergeTrace<T extends AgentTraceEntry>(entries: T[]): AgentTraceEntry[] {
  return entries;
}

export function confidenceFromMatchRatio(secretsLength: number, wordCount: number): number {
  if (secretsLength === 0) return 0.95;
  return Math.max(0.3, 1 - secretsLength / Math.max(wordCount, 1));
}

export { AgentStatus };
export type { AgentResult, InspectorOutput };
export type { AgentStatusType, AgentTraceEntry };
