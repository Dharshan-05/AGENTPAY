# AGENTPAY — 26: `apps/agent-runtime` Python Autonomous Agent Foundation

## 1. Agent Runtime Architecture

* `apps/agent-runtime` executes autonomous agent tools.
* **LLM Untrusted Rule**: Agent model outputs are parsed into structured tool intents and submitted to AGENTGUARD; agents cannot invoke payment APIs directly.
