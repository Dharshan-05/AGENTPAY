/**
 * AGENTPAY Backend API Contract TypeScript Definitions
 * Synchronized with backend apps/agent-runtime schemas
 */

// Canonical Response Envelope
export interface ApiSuccessEnvelope<T = any> {
  success: true;
  data: T;
  meta?: {
    request_id?: string;
    [key: string]: any;
  };
}

export interface ApiErrorEnvelope {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
  };
  meta?: {
    request_id?: string;
    [key: string]: any;
  };
}

export type ApiResponseEnvelope<T = any> = ApiSuccessEnvelope<T> | ApiErrorEnvelope;

// Authentication & Identity
export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface UserRegisterRequest {
  tenant_id: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface UserLoginResponseData {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    tenant_id: string;
    status: string;
  };
}

export interface UserMeResponseData {
  user_id: string;
  tenant_id: string;
  session_id: string;
  email: string;
  status: string;
  created_at: string;
  profile?: {
    id: string;
    first_name?: string;
    last_name?: string;
    display_name?: string;
  } | null;
}

// Agent Management
export interface AgentResponse {
  id: string;
  tenant_id: string;
  name: string;
  slug?: string;
  agent_type: string;
  description?: string;
  status: string;
  is_active?: boolean;
  created_at: string;
  updated_at?: string;
  risk_tier?: string;
  policy_binding?: string;
  transaction_count?: number;
  health_score?: number;
  credential_rotation_days?: number;
}

export interface AgentCreateRequest {
  name: string;
  agent_type: string;
  description?: string;
  owner?: string;
}

export interface AgentListResponse {
  agents: AgentResponse[];
  count: number;
  cursor?: {
    next_created_at?: string | null;
    next_id?: string | null;
  };
}

// Policy Governance (AGENTGUARD)
export interface PolicyRuleResponse {
  id: string;
  type: string;
  condition: string;
  threshold: string;
  action: 'ALLOW' | 'REVIEW' | 'BLOCK';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'ACTIVE' | 'DISABLED';
}

export interface PolicyResponse {
  id: string;
  tenant_id: string;
  policy_name?: string;
  name?: string;
  policy_type?: string;
  category?: string;
  description?: string;
  status: 'ACTIVE' | 'DISABLED' | 'INACTIVE';
  severity?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  violations_count?: number;
  agent_scope?: string;
  protected_fields?: string[];
  rules?: PolicyRuleResponse[];
  created_at?: string;
  updated_at?: string;
}

export interface PolicyCreateRequest {
  policy_name: string;
  policy_type: string;
  description?: string;
  rules?: any[];
}

export interface PolicyListResponse {
  items: PolicyResponse[];
  total: number;
  page: number;
  size: number;
}

// FraudGuard ML & Risk Intelligence
export interface FraudGuardInferenceRequest {
  transaction_id?: string;
  agent_id?: string;
  amount?: number;
  merchant?: string;
  category?: string;
  features?: Record<string, any>;
}

export interface FraudGuardInferenceResponse {
  risk_score: number;
  risk_band: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  decision: 'AUTHORIZED' | 'PENDING REVIEW' | 'BLOCKED';
  top_signal?: string;
  explainability?: { name: string; score: number }[];
  latency_ms?: number;
}

export interface RiskDecisionEvaluateRequest {
  transaction_id?: string;
  agent_id?: string;
  amount?: number;
  merchant?: string;
  category?: string;
  risk_score?: number;
  location?: string;
}

export interface RiskDecisionEvaluateResponse {
  decision_id?: string;
  decision: 'ALLOW' | 'REVIEW' | 'BLOCK';
  risk_score: number;
  risk_band: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  policy_applied?: string;
  explainability?: {
    identity?: string;
    spend?: string;
    merchant?: string;
    risk?: string;
  };
}

// Commerce & Transactions
export interface PurchaseRequestCreateRequest {
  agent_id?: string;
  product_id?: string;
  merchant_id?: string;
  amount: number;
  currency?: string;
  description?: string;
}

export interface PurchaseRequestResponse {
  id: string;
  tenant_id: string;
  agent_id?: string;
  amount: number;
  currency?: string;
  status: string;
  created_at: string;
  updated_at?: string;
}

export interface CommerceExecutionResponse {
  execution_id: string;
  purchase_request_id: string;
  status: string;
  decision?: string;
  message?: string;
}
