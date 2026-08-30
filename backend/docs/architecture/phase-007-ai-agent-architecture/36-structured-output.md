# AGENTPAY — 36: Pydantic & JSON Schema Validation Enforcement

## 1. Schema Validation Enforcement

100% of LLM reasoning outputs are generated using Pydantic / Zod JSON schema constraints (`response_format: { type: "json_object" }`). Free-form, unstructured natural language text responses are strictly prohibited for tool calling or intent proposal endpoints.
