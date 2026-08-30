# AGENTPAY — 13: Multi-Provider LLM Abstraction Layer

## 1. Provider Abstraction Interface

To prevent vendor lock-in, all model interactions implement an abstract `ILLMProvider` interface:

```typescript
export interface ILLMProvider {
  generateStructuredOutput<T>(
    prompt: PromptPayload,
    schema: ZodSchema<T>
  ): Promise<LLMResponse<T>>;
  
  generateEmbedding(text: string): Promise<number[]>;
}
```

---

## 2. Multi-Provider Fallback Topology

1. **Primary Provider**: OpenAI (`gpt-4o`).
2. **Secondary Provider**: Anthropic (`claude-3-5-sonnet`).
3. **Local Self-Hosted Option**: Ollama / vLLM (`llama-3-70b-instruct`).

If the primary provider times out ($> 5,000\text{ ms}$), the system fails over smoothly to the secondary provider while preserving session state.
