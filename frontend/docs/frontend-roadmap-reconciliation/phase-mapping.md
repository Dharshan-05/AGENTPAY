# PHASES 311–400 RECONCILIATION MAPPING TABLE

| Phase | Requirement | Existing Route(s) | Key Component(s) | Status | Notes |
|---|---|---|---|---|---|
| **311** | Next.js Setup | `/` (All Routes) | `app/layout.tsx`, App Router | COMPLETE | Next.js 15.5.24 App Router |
| **312** | React & TypeScript Configuration | All Files | `tsconfig.json`, Strict TS | COMPLETE | 0 TypeScript errors across project |
| **313** | Tailwind CSS Setup | All Files | `tailwind.config.ts`, `globals.css` | COMPLETE | Obsidian dark palette (`#020617`, `#050816`) |
| **314** | shadcn/ui Design System | All Files | `components/ui/` (`AGButton`, `AGBadge`, etc.) | COMPLETE | High-density dark theme primitives |
| **315** | Frontend Folder Architecture | Project Root | `app/`, `components/`, `docs/` | COMPLETE | Enterprise modular component design |
| **316** | API Client Layer | All Pages | Mock data layers & fetch abstractions | COMPLETE | Typed synthetic data schemas |
| **317** | State Management | All Pages | React Hooks (`useState`, `useMemo`) | COMPLETE | Clean tab & drawer state management |
| **318** | Authentication UI Foundation | `/settings`, `/session-control` | `SessionManager`, `AuthSettings` | COMPLETE | JWT session & API token management |
| **319** | JWT Session UI | `/sessions`, `/session-control` | `SessionTable`, `TokenInspect` | COMPLETE | Active session revocation & inspect |
| **320** | Global Layout & Navigation | All Routes | `AgentPayShell`, `AgentPaySidebar` | COMPLETE | Responsive sidebar with 104 badges |
| **321** | AgentPay Dashboard | `/`, `/command-center` | `DashboardMetrics`, `SystemOverview` | COMPLETE | Master executive metrics dashboard |
| **322** | AI Command Interface | `/ai-command-center` | `AICommandConsole`, `AgentPlanner` | COMPLETE | Natural language AI control plane |
| **323** | AI Chat Interface | `/ai-command-center` | `CarinaChatStream`, `TerminalFeed` | COMPLETE | Agentic conversational stream |
| **324** | Natural Language Purchase Input | `/ai-command-center` | `NaturalLanguagePromptBar` | COMPLETE | NL purchase intent parser |
| **325** | Intent Preview | `/payment-intents` | `IntentInspectorDrawer` | COMPLETE | Intent parameters & schema preview |
| **326** | Structured Intent Display | `/payment-intents` | `StructuredIntentCard` | COMPLETE | JSON intent schema & budget bounds |
| **327** | Intent Confirmation | `/payment-intents`, `/approvals` | `IntentConfirmModal` | COMPLETE | Intent sign-off & HITL trigger |
| **328** | Agent Planning UI | `/agents`, `/ai-command-center` | `AgentActionPlanner` | COMPLETE | Multi-step graph & dependency tree |
| **329** | Agent Execution UI | `/agents`, `/transactions` | `StepExecutionMonitor` | COMPLETE | Real-time tool call & step execution |
| **330** | Agent Activity Timeline | `/agents`, `/audit-logs` | `AgentActivityStream` | COMPLETE | Chronological action event log |
| **331** | Product Search UI | `/transaction-search`, `/product-catalog` | `ProductSearchBar` | COMPLETE | Full-text query & category filters |
| **332** | Product Filtering | `/product-catalog`, `/products` | `CatalogFilterDrawer` | COMPLETE | Price, SKU, merchant, stock filters |
| **333** | Product Details | `/products`, `/order-item-breakdown` | `ProductBreakdownDrawer` | COMPLETE | SKU metadata, specs & pricing |
| **334** | Product Comparison | `/product-catalog` | `ProductComparisonMatrix` | COMPLETE | Side-by-side SKU feature matrix |
| **335** | Product Ranking | `/product-catalog` | `RecommendationRankBadge` | COMPLETE | AI recommendation rank score |
| **336** | Product Recommendation | `/product-catalog` | `RecommendedProductsGrid` | COMPLETE | Agentic product recommendations |
| **337** | Inventory Availability | `/inventory`, `/inventory-control` | `InventoryStatusTable` | COMPLETE | Real-time warehouse stock status |
| **338** | Offer Optimization | `/discounts`, `/coupons` | `OfferOptimizationPanel` | COMPLETE | Coupon stacker & discount engine |
| **339** | Purchase Planning | `/orders`, `/order-management` | `OrderAssemblyBasket` | COMPLETE | Multi-item agent basket builder |
| **340** | Purchase Confirmation | `/checkout`, `/orders` | `PurchaseConfirmModal` | COMPLETE | Final checkout & order placement |
| **341** | AgentGuard Dashboard | `/agentguard` | `AgentGuardOverview` | COMPLETE | Primary autonomous safety plane |
| **342** | Agent Management UI | `/agents` | `AgentRegistryTable` | COMPLETE | Agent list, status, capabilities |
| **343** | Agent Creation UI | `/agents` | `ProvisionAgentModal` | COMPLETE | Agent provisioning & scope assignment |
| **344** | Agent Identity UI | `/agents`, `/kyc-verification` | `AgentIdentityCard` | COMPLETE | Agent identity hash & PKI keys |
| **345** | Agent Credential UI | `/api-keys`, `/tokenization-vault` | `AgentTokenVaultCard` | COMPLETE | Encrypted API keys & tokens |
| **346** | Agent Lifecycle UI | `/agents`, `/session-control` | `LifecycleStateBadge` | COMPLETE | Provisioned -> Active -> Revoked |
| **347** | Agent Activation UI | `/agents` | `ActivateAgentToggle` | COMPLETE | One-click agent activation |
| **348** | Agent Suspension UI | `/agents`, `/agentguard` | `EmergencyKillSwitch` | COMPLETE | Immediate agent suspension trigger |
| **349** | Agent Revocation UI | `/agents` | `RevokeAgentModal` | COMPLETE | Permanent credential destruction |
| **350** | Agent Permission UI | `/risk-rules`, `/agentguard` | `PermissionScopeMatrix` | COMPLETE | Granular API capability grants |
| **351** | RBAC Permission Management | `/tenant-isolation`, `/approvals` | `RbacMatrixTable` | COMPLETE | Multi-tenant role access matrix |
| **352** | Policy Management UI | `/agentguard` | `PolicyRuleEditor` | COMPLETE | Policy rule table & active controls |
| **353** | Spending Limit UI | `/agentguard`, `/agent-spend-velocity` | `SpendLimitGauge` | COMPLETE | Daily/Monthly spend limit caps |
| **354** | Transaction Threshold UI | `/agentguard`, `/risk-rules` | `TxnThresholdCard` | COMPLETE | Max single-transaction dollar limit |
| **355** | Category Restriction UI | `/agentguard` | `MccRestrictionMatrix` | COMPLETE | Allowed/Blocked MCC categories |
| **356** | Merchant Restriction UI | `/agentguard`, `/merchants` | `MerchantWhitelistTable` | COMPLETE | MID & domain whitelist/blacklist |
| **357** | Time-Based Policy UI | `/agentguard` | `OperatingHoursMatrix` | COMPLETE | Temporal spend restriction windows |
| **358** | Intent Verification UI | `/payment-intents`, `/agentguard` | `IntentSemanticCompliance` | COMPLETE | NL intent compliance evaluator |
| **359** | Behaviour Monitoring UI | `/agentguard`, `/fraud-anomaly-signals` | `BehaviorDriftChart` | COMPLETE | Behavioral variance score |
| **360** | Agent Trust Score UI | `/agentguard`, `/agents` | `AgentTrustIndexGauge` | COMPLETE | 0–100 Agent Trust Score gauge |
| **361** | FraudGuard Dashboard | `/fraudguard` | `FraudGuardOverview` | COMPLETE | Primary ML neural fraud detector |
| **362** | Fraud Probability UI | `/fraudguard`, `/fraud-anomaly-signals` | `FraudProbabilityMeter` | COMPLETE | 0.00%–100.00% fraud score meter |
| **363** | Transaction Risk Visualization | `/fraudguard`, `/transactions` | `TransactionRiskRadar` | COMPLETE | Risk breakdown radar & gauge |
| **364** | Behaviour Risk Visualization | `/fraudguard`, `/fraud-anomaly-signals` | `BehaviorAnomalyTimeline` | COMPLETE | Behavioral anomaly plot stream |
| **365** | Merchant Risk Visualization | `/merchants`, `/fraudguard` | `MerchantRiskProfile` | COMPLETE | MID chargeback & fraud ratio |
| **366** | Velocity Risk Visualization | `/agent-spend-velocity`, `/fraudguard` | `VelocitySpikeGraph` | COMPLETE | High-frequency transaction burst graph |
| **367** | Intent Risk Visualization | `/payment-intents`, `/fraudguard` | `PromptInjectionRiskCard` | COMPLETE | Semantic drift & prompt risk |
| **368** | Policy Risk Visualization | `/risk-rules`, `/agentguard` | `PolicyBreachHeatmap` | COMPLETE | Policy breach distribution |
| **369** | Agent Trust Risk Visualization | `/agentguard`, `/agents` | `TrustDecayCurve` | COMPLETE | Agent trust score degradation curve |
| **370** | Risk Factor Visualization | `/fraudguard` | `RiskFactorsList` | COMPLETE | Weighted risk contributor list |
| **371** | SHAP Feature Importance | `/fraudguard` | `ShapWaterfallChart` | COMPLETE | SHAP feature impact waterfall chart |
| **372** | Local Transaction Explanation | `/fraudguard`, `/transactions` | `LocalExplanationCard` | COMPLETE | Single transaction XAI rationale |
| **373** | Global Model Explanation | `/fraudguard` | `GlobalFeatureImportance` | COMPLETE | Global ML model feature importance |
| **374** | Why Blocked Interface | `/fraudguard`, `/transactions` | `WhyBlockedDiagnostic` | COMPLETE | "Why Blocked" diagnostic card |
| **375** | Why Reviewed Interface | `/fraudguard`, `/approvals` | `WhyReviewedDiagnostic` | COMPLETE | "Why Sent to HITL" rationale card |
| **376** | Transaction Dashboard | `/transactions` | `TransactionHeader`, `Metrics` | COMPLETE | Central transaction control plane |
| **377** | Transaction Search | `/transaction-search` | `TransactionSearchBar` | COMPLETE | Multi-parameter transaction search |
| **378** | Transaction Filters | `/transactions`, `/transaction-search` | `TransactionControls` | COMPLETE | Status, processor, risk filters |
| **379** | Transaction Details | `/transactions` | `TransactionInspector` | COMPLETE | Slide-over transaction drawer |
| **380** | Transaction Timeline | `/transactions` | `TransactionLifecycleStepper` | COMPLETE | Intent -> Auth -> Capture -> Settle |
| **381** | Payment Status UI | `/payments`, `/payment-attempts` | `PaymentStatusMatrix` | COMPLETE | Real-time payment status table |
| **382** | Payment Authorization UI | `/payments`, `/3ds-authentication` | `AuthorizationStatusCard` | COMPLETE | AVS, CVV, 3DS 2.0 auth step |
| **383** | Razorpay Checkout UI | `/checkout`, `/payment-methods` | `EmbeddedCheckoutCard` | COMPLETE | Embedded Razorpay/Stripe checkout |
| **384** | Payment Processing UI | `/payments`, `/gateway-routing` | `ProcessingStateMonitor` | COMPLETE | Live PSP processing pipeline |
| **385** | Payment Success UI | `/checkout`, `/payments` | `PaymentSuccessCard` | COMPLETE | Success confirmation & receipt |
| **386** | Payment Failure UI | `/checkout`, `/discrepancy-resolution` | `PaymentFailureDiagnostic` | COMPLETE | Failure reason & retry trigger |
| **387** | Payment Pending UI | `/payments`, `/payment-intents` | `AsyncProcessingListener` | COMPLETE | Async processing spinner & status |
| **388** | Payment Cancellation UI | `/payment-intents`, `/payments` | `CancelIntentModal` | COMPLETE | Intent cancellation & void trigger |
| **389** | Refund UI | `/refunds` | `IssueRefundModal` | COMPLETE | Partial & full refund processing |
| **390** | Payment History UI | `/payments`, `/payment-attempt-logs` | `PaymentHistoryLedger` | COMPLETE | Immutable payment log history |
| **391** | Review Queue UI | `/approvals` | `ApprovalQueueTable` | COMPLETE | Pending HITL review queue |
| **392** | Reviewer Dashboard | `/approvals` | `ReviewerMetricsCard` | COMPLETE | Queue SLA & reviewer metrics |
| **393** | Review Details | `/approvals` | `ApprovalInspectorDrawer` | COMPLETE | Slide-over review detail drawer |
| **394** | Risk Explanation for Reviewer | `/approvals`, `/fraudguard` | `ReviewerRiskExplanation` | COMPLETE | SHAP risk summary for reviewer |
| **395** | Approve Transaction UI | `/approvals` | `ApproveTransactionButton` | COMPLETE | Approval trigger with reason code |
| **396** | Reject Transaction UI | `/approvals` | `RejectTransactionButton` | COMPLETE | Rejection trigger with policy tag |
| **397** | Approval Expiration UI | `/approvals` | `TtlCountdownTimer` | COMPLETE | Approval expiration timer |
| **398** | Approval Status UI | `/approvals` | `ApprovalStatusBadge` | COMPLETE | APPROVED, REJECTED, EXPIRED |
| **399** | Reviewer Activity & Audit UI | `/approvals`, `/audit-trails` | `ReviewerAuditLog` | COMPLETE | Reviewer action timestamp log |
| **400** | Human Review Integration | `/approvals`, `/transactions` | `HitlIntegrationBridge` | COMPLETE | Seamless FraudGuard-to-HITL bridge |
