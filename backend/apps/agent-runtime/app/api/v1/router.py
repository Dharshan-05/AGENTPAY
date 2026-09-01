"""API v1 router composition."""

from fastapi import APIRouter

from app.api.v1.agents import agents_router
from app.api.v1.approvals import approvals_router
from app.api.v1.atim import atim_router
from app.api.v1.auth import auth_router
from app.api.v1.fraudguard import fraudguard_router
from app.api.v1.health import health_router
from app.api.v1.merchants import merchants_router
from app.api.v1.payments import payments_router
from app.api.v1.permissions import permissions_router
from app.api.v1.policies import policies_router
from app.api.v1.products import products_router
from app.api.v1.purchase_plans import purchase_plans_router
from app.api.v1.purchase_requests import purchase_requests_router
from app.api.v1.ready import ready_router
from app.api.v1.risk_decisions import risk_decisions_router
from app.api.v1.roles import roles_router
from app.api.v1.tools import tools_router
from app.api.v1.users import users_router

api_v1_router = APIRouter()

# Include infrastructure health, readiness, and authentication routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(ready_router)
api_v1_router.include_router(auth_router)

# Phase 112–113: RBAC Role & Permission Management
api_v1_router.include_router(roles_router)
api_v1_router.include_router(permissions_router)

# Phase 116–118: User Management, Profile & Preferences
api_v1_router.include_router(users_router)

# Phase 119–121: Agent Registry, Creation & Identity
api_v1_router.include_router(agents_router)

# Phase 157: Tool Registry Management
api_v1_router.include_router(tools_router)

# Phase 164–165 & 180–181: Commerce Engine - Products, Merchants, Plans & Requests
api_v1_router.include_router(merchants_router)
api_v1_router.include_router(products_router)
api_v1_router.include_router(purchase_plans_router)
api_v1_router.include_router(purchase_requests_router)

# Phase 185–186: AGENTGUARD Security Policy Management
api_v1_router.include_router(policies_router)

# Phases 261–265: FraudGuard ML, Risk Intelligence & Explainable AI Engine
api_v1_router.include_router(fraudguard_router)

# Phases 283–284: Risk & Decision Engine REST API & Audit Subsystem
api_v1_router.include_router(risk_decisions_router)

# Phases 293–294: Razorpay Webhook Ingestion & Signature Verification Boundary
api_v1_router.include_router(payments_router)

# Phases 304–305: Payment Approvals Workflow Boundary
api_v1_router.include_router(approvals_router)

# Phase 10 / Group 5: ATIM Transaction Intelligence, Evaluation & Observability Engine
api_v1_router.include_router(atim_router)

# Razorpay Buildathon Track 01: Agentic Commerce Engine & AI Models
from app.api.v1.commerce import router as commerce_router
from app.api.v1.ai import router as ai_router

api_v1_router.include_router(commerce_router)
api_v1_router.include_router(ai_router)


