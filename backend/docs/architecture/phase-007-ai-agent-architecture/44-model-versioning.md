# AGENTPAY — 44: Model Artifact & Prompt Registry Version Governance

## 1. Governance Registry

1. **Model Artifact Registry**: ML models tagged with semantic versions (`v1.0.0`) and stored with SHA-256 binary checksums.
2. **Prompt Template Registry**: System prompts versioned in Git (`prompts/v1/commerce_agent.ts`). Updating system prompts requires PR review and automated security regression testing.
