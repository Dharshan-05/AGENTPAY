# Phase 8: Intelligence & Real AI — Implementation Plan

**Goal:** Turn SentinelX into a genuinely intelligent AI Governance platform with real LLM integration, AI-powered features, and production-quality AI capabilities.

**Timeline:** Target completion before hackathon (Aug 7-8)

---

## Architecture Principles

1. **Hybrid AI + Rules**: Keep deterministic rule engine as the backbone; augment with LLM for reasoning, generation, and adaptive scoring
2. **Provider Agnostic**: Support OpenAI, Anthropic, Google (Gemini), OpenRouter, Ollama via unified interface
3. **Graceful Degradation**: Always fall back to rule-based behavior if LLM unavailable
4. **Streaming First**: All LLM responses stream via WebSocket for premium UX
5. **Token Transparency**: Track and display token usage, cost estimates, latency
6. **No Breaking Changes**: Preserve all existing API contracts and UI behavior

---

## Phase 8 Deliverables

### 1. LLM SDK Integration & Provider Infrastructure
- [ ] Add npm packages: `openai`, `@anthropic-ai/sdk`, `@google/generative-ai`, `openrouter` (or use OpenAI-compatible client)
- [ ] Create `LLMProvider` abstraction with unified interface
- [ ] Add provider health checking and automatic failover
- [ ] Implement token counting (tiktoken for OpenAI, custom for others)
- [ ] Add cost estimation per provider/model

### 2. Refactored LLMAdapterAgent
- [ ] Replace raw `fetch()` with SDK calls
- [ ] Add streaming support (Server-Sent Events / WebSocket)
- [ ] Emit real-time events via socket.io for frontend streaming
- [ ] Track tokens (prompt, completion, total), latency, cost per request
- [ ] Add request/response logging for audit
- [ ] Support system prompts, tool calling (for future)

### 3. AI-Powered Copilot (Replace Regex Engine)
- [ ] Create `CopilotAgent` or extend `answerCopilot()` with LLM
- [ ] Intent classification via LLM (not regex)
- [ ] Context injection: recent audit data, policy state, user profile
- [ ] Streaming response rendering in UI
- [ ] Conversation history support
- [ ] Structured output (JSON) for rich cards
- [ ] Fallback to rule-based if LLM fails

### 4. AI-Generated Explainability Reasoning
- [ ] New endpoint: `GET /api/explain/:decisionId/ai-reasoning`
- [ ] LLM generates human-readable reasoning from structured decision data
- [ ] Include: root cause, risk narrative, policy interpretation, remediation steps
- [ ] Cache results to avoid repeated calls

### 5. AI-Powered Policy Recommendations
- [ ] New endpoint: `POST /api/policies/recommend`
- [ ] Input: organization profile, recent violations, industry, regulations
- [ ] Output: suggested policy packs, custom rules, priority order
- [ ] One-click "Apply Recommendation" in Settings UI

### 6. Context-Aware Prompt Rewriting
- [ ] Enhance `RewriterAgent` with LLM-based rewriting
- [ ] Preserve semantic intent while removing sensitive data
- [ ] Support different rewrite styles: minimal, descriptive, placeholder
- [ ] A/B test: rule-based vs LLM rewrite quality

### 7. Adaptive Risk Scoring (Hybrid)
- [ ] New `AdaptiveRiskEngine` combining rule score + LLM assessment
- [ ] LLM evaluates context: user behavior, prompt intent, data sensitivity
- [ ] Weighted combination: 70% rules + 30% AI (configurable)
- [ ] Explainability: show both scores and reasoning

### 8. Executive Insights (AI-Generated)
- [ ] New endpoint: `GET /api/executive/insights`
- [ ] Input: time window, department filter
- [ ] Output: narrative summary, top risks, trend analysis, recommendations
- [ ] Scheduled generation (daily/weekly) with caching

### 9. AI-Generated Compliance Summaries
- [ ] New endpoint: `GET /api/compliance/summary`
- [ ] Per-regulation summary: coverage, violations, gaps, remediation
- [ ] Audit-ready PDF generation
- [ ] LLM translates technical findings to compliance language

### 10. Frontend: Streaming & Premium UX
- [ ] Copilot: streaming tokens with typewriter effect
- [ ] Thinking indicator with animated agent nodes
- [ ] Token usage display in responses
- [ ] Provider/model selector in settings
- [ ] Cost dashboard in analytics
- [ ] Error boundaries for LLM failures

---

## File Changes Map

### New Files
| Path | Purpose |
|------|---------|
| `apps/api/src/llm/providers.ts` | Provider abstraction & factory |
| `apps/api/src/llm/tokens.ts` | Token counting & cost estimation |
| `apps/api/src/llm/streaming.ts` | Streaming utilities |
| `apps/api/src/agents/copilot-agent.ts` | AI-powered copilot |
| `apps/api/src/agents/adaptive-risk.ts` | Hybrid risk scoring |
| `apps/api/src/routes/ai.ts` | New AI endpoints |
| `apps/web/src/hooks/useStreamingCopilot.ts` | Streaming hook |
| `apps/web/src/components/ui/ThinkingIndicator.tsx` | Animated thinking UI |

### Modified Files
| Path | Changes |
|------|---------|
| `apps/api/package.json` | Add LLM SDKs |
| `apps/api/src/agents/llm-adapter.ts` | SDK + streaming refactor |
| `apps/api/src/agents/rewriter.ts` | LLM-enhanced rewriting |
| `apps/api/src/server.ts` | Register new routes, copilot LLM integration |
| `apps/api/src/routes/enterprise.ts` | Add AI explainability, policy recs, insights |
| `apps/web/src/lib/api.ts` | New API methods |
| `apps/web/src/types/index.ts` | Extended types for LLM features |
| `apps/web/src/app/(dashboard)/copilot/page.tsx` | Streaming UI |
| `apps/web/src/app/(dashboard)/explain/page.tsx` | AI reasoning display |
| `apps/web/src/app/(dashboard)/settings/page.tsx` | LLM provider config |
| `apps/web/src/app/(dashboard)/analytics/page.tsx` | Token/cost charts |

---

## Implementation Order (Dependencies)

1. **Foundation** (parallel):
   - Add LLM SDKs to package.json
   - Create provider abstraction (`providers.ts`)
   - Token counting utilities (`tokens.ts`)

2. **Core Agent Refactor** (sequential):
   - Refactor `LLMAdapterAgent` to use SDKs + streaming
   - Add token tracking to pipeline output

3. **Copilot Intelligence** (depends on 2):
   - Build `CopilotAgent` with intent classification
   - Replace `answerCopilot()` in server.ts
   - Frontend streaming hook + UI

4. **Explainability & Insights** (depends on 2):
   - AI reasoning endpoint
   - Executive insights endpoint
   - Compliance summary endpoint

5. **Policy & Risk** (depends on 2):
   - Policy recommendations endpoint
   - Adaptive risk engine
   - LLM-enhanced rewriter

6. **Frontend Polish** (parallel, depends on 3-5):
   - Streaming copilot UI
   - AI reasoning in explain page
   - Token/cost analytics
   - Provider config in settings

7. **Verification**:
   - TypeScript strict check
   - Build verification
   - Runtime smoke test
   - Phase 8 report

---

## Environment Variables Required

```bash
# LLM Providers (at least one required for real AI)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
OPENROUTER_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Default provider/model
DEFAULT_LLM_PROVIDER=openrouter
DEFAULT_LLM_MODEL=openai/gpt-4o-mini

# Cost tracking (USD per 1M tokens)
OPENAI_COST_PER_M_INPUT=0.15
OPENAI_COST_PER_M_OUTPUT=0.60
ANTHROPIC_COST_PER_M_INPUT=0.25
ANTHROPIC_COST_PER_M_OUTPUT=1.25
GEMINI_COST_PER_M_INPUT=0.075
GEMINI_COST_PER_M_OUTPUT=0.30
OPENROUTER_COST_PER_M_INPUT=0.15
OPENROUTER_COST_PER_M_OUTPUT=0.60
```

---

## Success Criteria (Verification Gates)

| Gate | Command | Must Pass |
|------|---------|-----------|
| TypeScript | `cd apps/api && npx tsc --noEmit` | ✅ 0 errors |
| TypeScript | `cd apps/web && npx tsc --noEmit` | ✅ 0 errors |
| Build | `cd apps/web && npx next build` | ✅ Compiles, 23+ routes |
| Runtime | All 20+ pages return 200 | ✅ |
| Runtime | All 15+ API endpoints return 200 | ✅ |
| LLM Integration | `POST /api/scan` with real LLM | ✅ Streams, tracks tokens |
| Copilot | `POST /api/copilot` returns LLM answer | ✅ Streaming, structured data |
| Explainability | `GET /api/explain/:id/ai-reasoning` | ✅ Returns AI narrative |
| Policy Recs | `POST /api/policies/recommend` | ✅ Returns recommendations |
| Executive | `GET /api/executive/insights` | ✅ Returns narrative insights |
| Cost Tracking | Analytics shows token usage | ✅ |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM API failures | Graceful fallback to rule-based; simulate mode always works |
| Token costs | Cost estimation display; configurable limits; OpenRouter for cheaper models |
| Latency | Streaming UX hides latency; cache insights; async generation |
| Provider changes | Abstraction layer isolates provider-specific code |
| Breaking existing tests | Preserve all existing API contracts; add new endpoints, don't modify old |

---

## Next Phase Preview (Phase 9: Enterprise Features)

- Organization/Team management
- RBAC (Admin, SOC Analyst, Manager, Employee)
- Approval workflows
- Incident assignment & SLA timers
- Notification center + webhook simulation
- Policy versioning