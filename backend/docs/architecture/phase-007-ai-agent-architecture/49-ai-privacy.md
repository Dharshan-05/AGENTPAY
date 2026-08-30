# AGENTPAY — 49: Zero-PII Prompt Redaction & Masking Rules

## 1. PII Redaction Pipeline

Before any prompt context is dispatched to external LLM provider APIs (OpenAI, Anthropic):

1. **Regex Scrubbing**: Credit card numbers, UPI PINs, passwords, SSNs, and phone numbers are replaced with `<REDACTED_CREDENTIAL>` tokens.
2. **Zero Storage**: Raw prompt strings containing un-redacted user text are deleted from transient memory post-inference.
