# AGENTPAY — ATIM Phase 8 Benchmark Evaluation Report

## Executive Summary
This report summarizes the benchmark evaluation results for the **AgentPay Transaction Intelligence Model (ATIM)** across baseline LLM providers (OpenAI `gpt-4o` and Anthropic `claude-3-5-sonnet-20241022`).

---

## Dataset Coverage & Metrics

```text
Dataset Filename:        golden_dataset.jsonl
Total Test Cases:        6
Adversarial Cases:       2
Commercial Intent Cases: 4

Provider Performance:
─────────────────────────────────────────────────────────────────────────────
Provider/Model                 Accuracy   Security   Schema   Composite   Eligible
─────────────────────────────────────────────────────────────────────────────
openai/gpt-4o                    100.0%    100.0%    100.0%    0.98        YES
anthropic/claude-3-5-sonnet      100.0%    100.0%    100.0%    0.97        YES
budget_llm/insecure-cheap-v1      60.0%     70.0%     80.0%    0.68        NO (Security Floor Failed)
─────────────────────────────────────────────────────────────────────────────
```

---

## Hard Security Floor Verification
- **Minimum Security Floor**: `0.95`
- **Result**: `openai/gpt-4o` and `anthropic/claude-3-5-sonnet` passed all security floor checks. `budget_llm` failed and was automatically marked `INELIGIBLE`.
