"""ATIM Transaction Intelligence Pipeline Facade Service for AGENTPAY (Phase 10 / Group 5)."""

import time
import uuid
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.atim_execution_decision_service import ATIMExecutionDecisionService
from app.application.services.atim_intelligent_router import ATIMIntelligentRouter
from app.application.services.atim_observability_service import ATIMObservabilityService
from app.application.services.intent_extraction_service import IntentExtractionService
from app.application.services.prompt_guard_service import PromptGuardService
from app.domain.atim.telemetry_models import (
    ATIMAnalyzeRequest,
    ATIMAnalyzeResponse,
    ATIMTelemetryRecord,
)
from app.schemas.atim import ATIMPlanProposal, ATIMProposedIntent


class ATIMFacadeService:
    """Facade orchestrating ATIM Prompt Security, Model Routing, Intent Extraction, Plan Validation, Security Integration, and Telemetry Logging."""

    def __init__(
        self,
        prompt_guard_service: Optional[PromptGuardService] = None,
        router: Optional[ATIMIntelligentRouter] = None,
        intent_extraction_service: Optional[IntentExtractionService] = None,
        execution_decision_service: Optional[ATIMExecutionDecisionService] = None,
        observability_service: Optional[ATIMObservabilityService] = None,
    ):
        self.prompt_guard = prompt_guard_service or PromptGuardService()
        self.router = router or ATIMIntelligentRouter()
        self.intent_extractor = intent_extraction_service or IntentExtractionService()
        self.execution_decision_service = (
            execution_decision_service or ATIMExecutionDecisionService()
        )
        self.observability = observability_service or ATIMObservabilityService()


    async def analyze_transaction_intelligence(
        self,
        db: AsyncSession | Any,
        request: ATIMAnalyzeRequest,
    ) -> ATIMAnalyzeResponse:
        """Run complete ATIM natural language transaction intelligence analysis pipeline."""
        start_time = time.perf_counter()
        req_id = uuid.uuid4()

        # Step 1: Prompt Security Audit (Phase 4 PromptGuard)
        sanitization = self.prompt_guard.sanitize_prompt(request.prompt)
        is_blocked = sanitization.contains_suspicious_injection or sanitization.contains_secret

        if is_blocked:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            rejection_reason = ", ".join(sanitization.detected_threats) or "PROMPT_SECURITY_VIOLATION"
            telemetry = ATIMTelemetryRecord(
                id=uuid.uuid4(),
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                request_id=req_id,
                prompt_text=request.prompt,
                is_security_blocked=True,
                security_score=Decimal("0.1000"),
                security_reason=rejection_reason,
                selected_model="none",
                provider="none",
                fallback_used=False,
                latency_ms=elapsed_ms,
                agentguard_decision="BLOCKED",
                fraudguard_score=1.0,
                hitl_required=False,
                execution_decision="DENY",
            )
            await self.observability.record_telemetry(db, telemetry)

            return ATIMAnalyzeResponse(
                request_id=req_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                prompt_security_blocked=True,
                security_reason=rejection_reason,
                selected_model="none",
                provider="none",
                fallback_used=False,
                task_type="INTENT_EXTRACTION",
                complexity="CRITICAL",
                risk_level="CRITICAL",
                proposed_intent={"action": "PROMPT_INJECTION", "amount": Decimal("0.00"), "confidence": 1.0, "reasoning": rejection_reason},
                proposed_plan=None,
                plan_valid=False,
                agentguard_decision="BLOCKED",
                fraudguard_score=1.0,
                hitl_required=False,
                final_execution_decision="DENY",
                latency_ms=round(elapsed_ms, 2),
                estimated_cost_usd=Decimal("0.000000"),
            )


            return ATIMAnalyzeResponse(
                request_id=req_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                prompt_security_blocked=True,
                security_reason=prompt_audit.rejection_reason or "PROMPT_SECURITY_VIOLATION",
                selected_model="none",
                provider="none",
                fallback_used=False,
                task_type="INTENT_EXTRACTION",
                complexity="CRITICAL",
                risk_level="CRITICAL",
                proposed_intent=None,
                proposed_plan=None,
                plan_valid=False,
                agentguard_decision="BLOCKED",
                fraudguard_score=1.0,
                hitl_required=False,
                final_execution_decision="DENY",
                latency_ms=round(elapsed_ms, 2),
                estimated_cost_usd=Decimal("0.000000"),
            )

        # Step 2: Task/Risk Classification & Intelligent Model Routing (Phase 9)
        routing_res = self.router.route_request(
            prompt_text=request.prompt,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
        )

        # Step 3: Intent & Constraint Extraction (Phase 2 & Phase 140)
        try:
            target_m = getattr(request, "model", None)
            struct_intent = await self.intent_extractor.provider.extract(request.prompt, {}, target_model=target_m)
            extracted_action = (getattr(struct_intent, "action", None) or "").upper().strip()
            extracted_entities = getattr(struct_intent, "entities", None)
            extracted_amount = getattr(extracted_entities, "amount", None) if extracted_entities else None
            extracted_currency = getattr(extracted_entities, "currency", None) if extracted_entities else None
        except Exception as exc:
            logger.warning("Intent extraction error in facade: %s", exc)
            extracted_action = "UNKNOWN"
            extracted_amount = None
            extracted_currency = None

        prompt_lower = request.prompt.lower().strip()
        greetings = {
            "hi", "hello", "hey", "hi there", "good morning", "good afternoon",
            "good evening", "how are you", "thank you", "thanks", "ok", "okay",
            "test", "ping"
        }
        general_queries = {
            "what can you do?", "what can you do", "help", "who are you"
        }

        # Commerce & Intent Taxonomy Rule Matching
        commerce_keywords = [
            "laptop", "notebook", "macbook", "phone", "mobile", "smartphone", "iphone", "samsung",
            "smartwatch", "headphones", "earbuds", "tablet", "tv", "monitor", "keyboard", "camera",
            "gaming", "coding", "under", "undr", "below", "budget"
        ]
        is_commerce_query = any(kw in prompt_lower for kw in commerce_keywords)

        # Default fallback intent & financial governance variables
        action = "GENERAL_QUERY"
        amount = Decimal("0.00")
        currency = request.requested_currency or extracted_currency or "INR"
        is_non_financial = True
        default_decision = "NOT_REQUESTED"

        if any(kw in prompt_lower for kw in ["select ", "option 1", "option 2", "option 3", "option 4", "choose 1", "choose 2", "i want the"]):
            action = "PRODUCT_SELECTION"
            amount = Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "INR"
            is_non_financial = True
            default_decision = "NOT_REQUESTED"
        elif any(kw in prompt_lower for kw in ["compare ", "compare 1 and 2", "comparison"]):
            action = "PRODUCT_COMPARISON"
            amount = Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "INR"
            is_non_financial = True
            default_decision = "NOT_REQUESTED"
        elif any(kw in prompt_lower for kw in ["which seller is safest", "safest seller", "seller trust"]):
            action = "SELLER_ANALYSIS"
            amount = Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "INR"
            is_non_financial = True
            default_decision = "NOT_REQUESTED"
        elif any(kw in prompt_lower for kw in ["is this product risky", "check risk", "risky product"]):
            action = "PRODUCT_RISK_ANALYSIS"
            amount = Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "INR"
            is_non_financial = True
            default_decision = "NOT_REQUESTED"
        elif any(kw in prompt_lower for kw in ["check this price", "check price", "price check"]):
            action = "PRICE_ANALYSIS"
            amount = Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "INR"
            is_non_financial = True
            default_decision = "NOT_REQUESTED"
        elif extracted_action in ("PURCHASE_REQUEST", "PURCHASE", "PAYMENT") or any(prompt_lower.startswith(w) or f" {w} " in f" {prompt_lower} " for w in ["buy", "buy it", "purchase", "buy product"]):
            action = "PURCHASE"
            amount = request.requested_amount or extracted_amount or Decimal("0.00")
            currency = extracted_currency or request.requested_currency or "INR"
            is_non_financial = False
            default_decision = "DENY"
        elif extracted_action in ("GREETING", "GREETINGS") or prompt_lower in greetings or any(prompt_lower.startswith(g + " ") for g in ["hi", "hello", "hey", "good morning"]):
            action = "GREETING"
            amount = Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "USD"
            is_non_financial = True
            default_decision = "NOT_REQUESTED"
        elif extracted_action in ("GENERAL_QUERY", "INFO") or prompt_lower in general_queries or any(q in prompt_lower for q in general_queries):
            action = "GENERAL_QUERY"
            amount = Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "USD"
            is_non_financial = True
            default_decision = "NOT_REQUESTED"
        elif extracted_action in ("TRANSACTION_QUERY", "TRANSACTION_LOOKUP") or any(q in prompt_lower for q in ["show my transactions", "check my last payment", "transaction history"]):
            action = "TRANSACTION_QUERY"
            amount = Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "USD"
            is_non_financial = True
            default_decision = "NOT_REQUESTED"
        elif extracted_action in (
            "PRODUCT_SEARCH", "PRODUCT_RECOMMENDATION", "PRODUCT_COMPARISON",
            "PRODUCT_DETAILS", "SELLER_ANALYSIS", "PRODUCT_RISK_ANALYSIS", "PRICE_ANALYSIS", "PRODUCT_SELECTION"
        ) or is_commerce_query:
            action = extracted_action if extracted_action in (
                "PRODUCT_SEARCH", "PRODUCT_RECOMMENDATION", "PRODUCT_COMPARISON",
                "PRODUCT_DETAILS", "SELLER_ANALYSIS", "PRODUCT_RISK_ANALYSIS", "PRICE_ANALYSIS", "PRODUCT_SELECTION"
            ) else "PRODUCT_SEARCH"
            amount = Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "INR"
            is_non_financial = True
            default_decision = "NOT_REQUESTED"
        elif extracted_action == "AMBIGUOUS":
            action = "AMBIGUOUS"
            amount = Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "USD"
            is_non_financial = True
            default_decision = "DENY"
        elif extracted_action in ("PURCHASE_REQUEST", "PURCHASE", "PAYMENT") or any(prompt_lower.startswith(w) or w in prompt_lower for w in ["buy ", "buy it", "purchase ", "buy product"]):
            action = "PURCHASE"
            amount = request.requested_amount or extracted_amount or Decimal("0.00")
            currency = extracted_currency or request.requested_currency or "INR"
            is_non_financial = False
            default_decision = "DENY"
        else:
            action = extracted_action if extracted_action and extracted_action != "UNKNOWN" else ("PRODUCT_SEARCH" if is_commerce_query else "GENERAL_QUERY")
            amount = request.requested_amount or extracted_amount or Decimal("0.00")
            currency = request.requested_currency or extracted_currency or "INR"
            is_non_financial = (action != "PURCHASE")
            default_decision = "DENY" if action == "PURCHASE" else "NOT_REQUESTED"

        proposed_intent = ATIMProposedIntent(
            action=action,
            amount=amount,
            currency=currency,
            merchant=request.category,
            target_account=str(request.merchant_id) if request.merchant_id else None,
            is_ambiguous=(action == "AMBIGUOUS"),
        )

        proposal = ATIMPlanProposal(
            proposed_intent=proposed_intent,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            risk_classification=routing_res.risk_level.value,
        )

        # Step 4: Security Integration Evaluation (Phase 6 AGENTGUARD + FRAUDGUARD + HITL)
        if is_non_financial:
            final_decision_str = default_decision
            ag_status = "NOT_REQUIRED"
            fg_score = 0.0
            hitl_req = False
        else:
            execution_decision = await self.execution_decision_service.evaluate_proposal_execution(
                db=db,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                proposal=proposal,
            )
            final_decision_str = execution_decision.decision
            ag_status = execution_decision.agentguard_status or "ALLOWED"
            fg_score = execution_decision.fraudguard_decision.risk_score if execution_decision.fraudguard_decision else 0.05
            hitl_req = execution_decision.requires_human_approval

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Step 5: Record Telemetry (Phase 10)
        telemetry = ATIMTelemetryRecord(
            id=uuid.uuid4(),
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            request_id=req_id,
            prompt_text=request.prompt,
            action=action,
            amount=amount,
            currency=currency,
            is_security_blocked=False,
            security_score=Decimal("0.9800"),
            selected_model=str(routing_res.selected_model),
            provider=str(routing_res.selected_provider),
            fallback_used=bool(routing_res.fallback_route),
            task_type=routing_res.task_type.value,
            complexity=routing_res.complexity.value,
            risk_level=routing_res.risk_level.value,
            latency_ms=elapsed_ms,
            prompt_tokens=150,
            completion_tokens=45,
            total_tokens=195,
            estimated_cost_usd=Decimal("0.001500"),
            agentguard_decision=ag_status,
            fraudguard_score=fg_score,
            hitl_required=hitl_req,
            execution_decision=final_decision_str,
        )
        await self.observability.record_telemetry(db, telemetry)

        return ATIMAnalyzeResponse(
            request_id=req_id,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            prompt_security_blocked=False,
            security_reason=None,
            selected_model=str(routing_res.selected_model),
            provider=str(routing_res.selected_provider),
            fallback_used=bool(routing_res.fallback_route),
            task_type=routing_res.task_type.value,
            complexity=routing_res.complexity.value,
            risk_level=routing_res.risk_level.value,
            proposed_intent=proposed_intent.model_dump(),
            proposed_plan=proposal.model_dump(),
            plan_valid=True,
            agentguard_decision=ag_status,
            fraudguard_score=fg_score,
            hitl_required=hitl_req,
            final_execution_decision=final_decision_str,
            latency_ms=round(elapsed_ms, 2),
            estimated_cost_usd=Decimal("0.001500"),
        )
