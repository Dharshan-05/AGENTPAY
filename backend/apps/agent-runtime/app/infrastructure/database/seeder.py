"""Production-Safe Deterministic Seed Engine for AGENTPAY (Phase 078)."""

import logging
import os
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.authorization.permissions_registry import ALL_PERMISSIONS
from app.infrastructure.database.models import (
    Agent,
    AttackSimulation,
    AuditLog,
    Inventory,
    Merchant,
    Offer,
    PaymentOrder,
    PaymentTransaction,
    Permission,
    PolicyRule,
    Product,
    ProductCategory,
    RiskDecisionAudit,
    Role,
    RolePermission,
    SecurityEvent,
    SecurityPolicy,
    User,
    UserProfile,
    UserRole,
    PurchaseIntent,
    PurchasePlan,
    FraudPrediction,
    XAIExplanation,
    ToolExecutionAudit,
)

logger = logging.getLogger("agentpay.infrastructure.database.seeder")

# Deterministic Seed Namespaces & Identifiers
SEED_TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
SEED_USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000002")
SEED_MERCHANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000003")
SEED_AGENT_ID = uuid.UUID("00000000-0000-4000-a000-000000000004")
SEED_PRODUCT_ID = uuid.UUID("00000000-0000-4000-a000-000000000005")
SEED_CATEGORY_ID = uuid.UUID("00000000-0000-4000-a000-000000000006")
SEED_OFFER_ID = uuid.UUID("00000000-0000-4000-a000-000000000007")
SEED_POLICY_ID = uuid.UUID("00000000-0000-4000-a000-000000000008")
SEED_RULE_ID = uuid.UUID("00000000-0000-4000-a000-000000000009")
SEED_ORDER_ID = uuid.UUID("00000000-0000-4000-a000-000000000010")
SEED_TXN_ID = uuid.UUID("00000000-0000-4000-a000-000000000011")


class ProductionSeedingProhibitedError(RuntimeError):
    """Raised when seed execution is attempted in a production environment."""


def verify_seed_environment(env_name: str | None = None) -> str:
    """Enforce strict production safety rules prior to seeding."""
    raw_env = env_name or os.getenv("AGENTPAY_ENV") or "development"
    env = raw_env.lower()

    if env in ("production", "prod", "live"):
        raise ProductionSeedingProhibitedError(
            f"Seeding is strictly prohibited in production environment ('{env}')."
        )
    return env


class DatabaseSeeder:
    """Deterministic, idempotent seed manager for development, testing, and demo environments."""

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID = SEED_TENANT_ID) -> None:
        self.session = session
        self.tenant_id = tenant_id

    async def seed_all(self, env_name: str | None = None) -> dict[str, int]:
        """Execute complete idempotent database seeding in correct foreign key order."""
        verify_seed_environment(env_name)

        counts: dict[str, int] = {}
        counts["users"] = await self._seed_users()
        counts["rbac"] = await self._seed_rbac()
        counts["merchants"] = await self._seed_merchants()
        counts["product_categories"] = await self._seed_product_categories()
        counts["products"] = await self._seed_products()
        counts["offers"] = await self._seed_offers()
        counts["inventory"] = await self._seed_inventory()
        counts["agents"] = await self._seed_agents()
        counts["security_policies"] = await self._seed_security_policies()
        counts["policy_rules"] = await self._seed_policy_rules()
        counts["purchase_intents"] = await self._seed_purchase_intents()
        counts["purchase_plans"] = await self._seed_purchase_plans()
        counts["fraud_predictions"] = await self._seed_fraud_predictions()
        counts["xai_explanations"] = await self._seed_xai_explanations()
        counts["payment_orders"] = await self._seed_payment_orders()
        counts["payment_transactions"] = await self._seed_payment_transactions()
        counts["risk_decision_audits"] = await self._seed_risk_decision_audits()
        counts["audit_logs"] = await self._seed_audit_logs()
        counts["security_events"] = await self._seed_security_events()
        counts["attack_simulations"] = await self._seed_attack_simulations()
        counts["tool_execution_audit"] = await self._seed_tool_execution_audit()

        await self.session.commit()
        return counts

    async def _seed_users(self) -> int:
        """Seed realistic development identities."""
        user_data = [
            (SEED_USER_ID, "seed.reviewer@agentpay.internal", "Seed System", "Reviewer"),
            (uuid.UUID("00000000-0000-4000-a000-000000000020"), "admin@agentpay.local", "Admin", "Superuser"),
            (uuid.UUID("00000000-0000-4000-a000-000000000021"), "security@agentpay.local", "Security", "Analyst"),
            (uuid.UUID("00000000-0000-4000-a000-000000000022"), "fraud@agentpay.local", "Fraud", "Analyst"),
            (uuid.UUID("00000000-0000-4000-a000-000000000023"), "merchant1@agentpay.local", "Amazon", "Operator"),
            (uuid.UUID("00000000-0000-4000-a000-000000000024"), "merchant2@agentpay.local", "TechNova", "Operator"),
            (uuid.UUID("00000000-0000-4000-a000-000000000025"), "user1@agentpay.local", "Alice", "Buyer"),
            (uuid.UUID("00000000-0000-4000-a000-000000000026"), "user2@agentpay.local", "Bob", "Buyer"),
            (uuid.UUID("00000000-0000-4000-a000-000000000027"), "auditor@agentpay.local", "Compliance", "Auditor"),
        ]

        added = 0
        for uid, email, fname, lname in user_data:
            res = await self.session.execute(
                select(User).where(User.tenant_id == self.tenant_id, User.id == uid)
            )
            if res.scalar_one_or_none() is None:
                user = User(
                    id=uid,
                    tenant_id=self.tenant_id,
                    email=email,
                    password_hash="$argon2id$v=19$m=65536,t=3,p=4$synthetic_seed_hash",
                    status="active",
                )
                profile = UserProfile(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    user_id=uid,
                    first_name=fname,
                    last_name=lname,
                    display_name=f"{fname} {lname}",
                )
                self.session.add(user)
                self.session.add(profile)
                added += 1
        return added

    async def _seed_merchants(self) -> int:
        """Seed 8 realistic merchant entities."""
        merchants = [
            (SEED_MERCHANT_ID, "Seed Commerce Merchant", "merch-seed-001"),
            (uuid.UUID("00000000-0000-4000-a000-000000000030"), "Amazon Demo Store", "amazon-demo-store"),
            (uuid.UUID("00000000-0000-4000-a000-000000000031"), "TechNova Electronics", "technova-electronics"),
            (uuid.UUID("00000000-0000-4000-a000-000000000032"), "CloudMart Web Services", "cloudmart-web-services"),
            (uuid.UUID("00000000-0000-4000-a000-000000000033"), "TravelSphere Global", "travelsphere-global"),
            (uuid.UUID("00000000-0000-4000-a000-000000000034"), "FoodExpress Delivery", "foodexpress-delivery"),
            (uuid.UUID("00000000-0000-4000-a000-000000000035"), "DigitalBooks Direct", "digitalbooks-direct"),
            (uuid.UUID("00000000-0000-4000-a000-000000000036"), "AI Tools Marketplace", "ai-tools-marketplace"),
            (uuid.UUID("00000000-0000-4000-a000-000000000037"), "Global Gadgets", "global-gadgets"),
        ]

        added = 0
        for mid, name, slug in merchants:
            res = await self.session.execute(
                select(Merchant).where(Merchant.tenant_id == self.tenant_id, Merchant.id == mid)
            )
            if res.scalar_one_or_none() is None:
                merchant = Merchant(
                    id=mid,
                    tenant_id=self.tenant_id,
                    name=name,
                    slug=slug,
                    status="active",
                )
                self.session.add(merchant)
                added += 1
        return added

    async def _seed_product_categories(self) -> int:
        """Seed 8 product categories."""
        categories = [
            (SEED_CATEGORY_ID, SEED_MERCHANT_ID, "Seed Software Services", "cat-seed-001"),
            (uuid.UUID("00000000-0000-4000-a000-000000000040"), uuid.UUID("00000000-0000-4000-a000-000000000031"), "Consumer Electronics", "cat-electronics"),
            (uuid.UUID("00000000-0000-4000-a000-000000000041"), uuid.UUID("00000000-0000-4000-a000-000000000032"), "Cloud Infrastructure & Hosting", "cat-cloud-hosting"),
            (uuid.UUID("00000000-0000-4000-a000-000000000042"), uuid.UUID("00000000-0000-4000-a000-000000000033"), "Travel & Accommodations", "cat-travel"),
            (uuid.UUID("00000000-0000-4000-a000-000000000043"), uuid.UUID("00000000-0000-4000-a000-000000000034"), "Food & Dining", "cat-food"),
            (uuid.UUID("00000000-0000-4000-a000-000000000044"), uuid.UUID("00000000-0000-4000-a000-000000000035"), "E-Books & Publications", "cat-books"),
            (uuid.UUID("00000000-0000-4000-a000-000000000045"), uuid.UUID("00000000-0000-4000-a000-000000000036"), "AI API & Model Credits", "cat-ai-credits"),
            (uuid.UUID("00000000-0000-4000-a000-000000000046"), uuid.UUID("00000000-0000-4000-a000-000000000030"), "Subscriptions & Memberships", "cat-subscriptions"),
        ]

        added = 0
        for cid, mid, name, slug in categories:
            res = await self.session.execute(
                select(ProductCategory).where(
                    ProductCategory.tenant_id == self.tenant_id,
                    ProductCategory.id == cid,
                )
            )
            if res.scalar_one_or_none() is None:
                cat = ProductCategory(
                    id=cid,
                    tenant_id=self.tenant_id,
                    merchant_id=mid,
                    name=name,
                    slug=slug,
                    status="active",
                )
                self.session.add(cat)
                added += 1
        return added

    async def _seed_products(self) -> int:
        """Seed 25 realistic products across categories."""
        products = [
            (SEED_PRODUCT_ID, SEED_MERCHANT_ID, "Seed Agent Execution Token Pass", "PROD-SEED-001", Decimal("49.99")),
            (uuid.UUID("00000000-0000-4000-a000-000000000050"), uuid.UUID("00000000-0000-4000-a000-000000000031"), "MacBook Pro M3 Max Demo", "PROD-ELECTRONICS-001", Decimal("3499.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000051"), uuid.UUID("00000000-0000-4000-a000-000000000031"), "ThinkPad X1 Carbon Demo", "PROD-ELECTRONICS-002", Decimal("1899.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000052"), uuid.UUID("00000000-0000-4000-a000-000000000031"), "NVIDIA RTX 4090 Workstation GPU", "PROD-ELECTRONICS-003", Decimal("1599.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000053"), uuid.UUID("00000000-0000-4000-a000-000000000036"), "Claude 3.5 Sonnet API Credits 100K", "PROD-AI-001", Decimal("100.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000054"), uuid.UUID("00000000-0000-4000-a000-000000000036"), "GPT-4o Enterprise Token Pass", "PROD-AI-002", Decimal("250.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000055"), uuid.UUID("00000000-0000-4000-a000-000000000032"), "AWS Cloud Compute Fleet Voucher", "PROD-CLOUD-001", Decimal("500.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000056"), uuid.UUID("00000000-0000-4000-a000-000000000032"), "Google Cloud BigQuery Processing License", "PROD-CLOUD-002", Decimal("300.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000057"), uuid.UUID("00000000-0000-4000-a000-000000000030"), "JetBrains All Products Pack Annual", "PROD-SAAS-001", Decimal("289.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000058"), uuid.UUID("00000000-0000-4000-a000-000000000030"), "Docker Pro Team Annual Subscription", "PROD-SAAS-002", Decimal("120.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000059"), uuid.UUID("00000000-0000-4000-a000-000000000033"), "International Business Class Flight Pass", "PROD-TRAVEL-001", Decimal("1250.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000060"), uuid.UUID("00000000-0000-4000-a000-000000000033"), "Five-Star Luxury Hotel 3-Night Package", "PROD-TRAVEL-002", Decimal("850.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000061"), uuid.UUID("00000000-0000-4000-a000-000000000037"), "Sony WH-1000XM5 Noise Canceling Headphones", "PROD-GADGETS-001", Decimal("399.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000062"), uuid.UUID("00000000-0000-4000-a000-000000000037"), "iPhone 16 Pro Max 512GB", "PROD-GADGETS-002", Decimal("1399.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000063"), uuid.UUID("00000000-0000-4000-a000-000000000037"), "Keychron Q1 Pro Wireless Mechanical Keyboard", "PROD-GADGETS-003", Decimal("199.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000064"), uuid.UUID("00000000-0000-4000-a000-000000000030"), "CrowdStrike Falcon Endpoint Security", "PROD-SEC-001", Decimal("450.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000065"), uuid.UUID("00000000-0000-4000-a000-000000000032"), "Datadog Infrastructure Monitoring 1-Yr", "PROD-MONITOR-001", Decimal("600.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000066"), uuid.UUID("00000000-0000-4000-a000-000000000030"), "GitHub Enterprise Server License", "PROD-DEV-001", Decimal("250.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000067"), uuid.UUID("00000000-0000-4000-a000-000000000030"), "Veracode Application Security Audit Pass", "PROD-SEC-002", Decimal("1500.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000068"), uuid.UUID("00000000-0000-4000-a000-000000000036"), "Pinecone Vector DB Enterprise Plan", "PROD-AI-003", Decimal("400.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000069"), uuid.UUID("00000000-0000-4000-a000-000000000036"), "LangSmith LLM Tracing Tier", "PROD-AI-004", Decimal("150.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000070"), uuid.UUID("00000000-0000-4000-a000-000000000032"), "Supabase Enterprise Database Bundle", "PROD-DB-001", Decimal("299.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000071"), uuid.UUID("00000000-0000-4000-a000-000000000030"), "Tailwind UI Pro License", "PROD-UI-001", Decimal("299.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000072"), uuid.UUID("00000000-0000-4000-a000-000000000032"), "Vercel Enterprise Pro Deployment Pass", "PROD-HOST-001", Decimal("200.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000073"), uuid.UUID("00000000-0000-4000-a000-000000000030"), "Postman Enterprise Team Workspace", "PROD-API-001", Decimal("480.00")),
        ]

        added = 0
        for pid, mid, name, sku, price in products:
            res = await self.session.execute(
                select(Product).where(Product.tenant_id == self.tenant_id, Product.id == pid)
            )
            if res.scalar_one_or_none() is None:
                prod = Product(
                    id=pid,
                    tenant_id=self.tenant_id,
                    merchant_id=mid,
                    name=name,
                    sku=sku,
                    price=price,
                    currency_code="USD",
                    status="active",
                )
                self.session.add(prod)
                added += 1
        return added

    async def _seed_inventory(self) -> int:
        """Seed inventory records for all 25 products."""
        res_prods = await self.session.execute(
            select(Product).where(Product.tenant_id == self.tenant_id)
        )
        products = res_prods.scalars().all()

        added = 0
        for i, prod in enumerate(products):
            res = await self.session.execute(
                select(Inventory).where(
                    Inventory.tenant_id == self.tenant_id,
                    Inventory.product_id == prod.id,
                )
            )
            if res.scalar_one_or_none() is None:
                qty = 500 if i % 4 != 3 else 0  # Include out-of-stock for realism
                inv = Inventory(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    merchant_id=prod.merchant_id,
                    product_id=prod.id,
                    quantity=qty,
                    reserved_quantity=5 if qty > 0 else 0,
                    available_quantity=max(0, qty - 5),
                    reorder_level=10,
                    status="active" if qty > 0 else "out_of_stock",
                )
                self.session.add(inv)
                added += 1
        return added

    async def _seed_offers(self) -> int:
        """Seed 10 promotional offers."""
        offers = [
            (SEED_OFFER_ID, SEED_MERCHANT_ID, SEED_PRODUCT_ID, "Seed Agent Runtime Trial Discount", "offer-seed-001", Decimal("44.99")),
            (uuid.UUID("00000000-0000-4000-a000-000000000080"), uuid.UUID("00000000-0000-4000-a000-000000000036"), uuid.UUID("00000000-0000-4000-a000-000000000053"), "10% AI Developer Discount", "offer-ai-dev-10", Decimal("90.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000081"), uuid.UUID("00000000-0000-4000-a000-000000000032"), uuid.UUID("00000000-0000-4000-a000-000000000055"), "Cloud Fleet Startup Grant Offer", "offer-cloud-grant", Decimal("425.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000082"), uuid.UUID("00000000-0000-4000-a000-000000000033"), uuid.UUID("00000000-0000-4000-a000-000000000059"), "Business Travel Agent Special", "offer-travel-special", Decimal("1100.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000083"), uuid.UUID("00000000-0000-4000-a000-000000000030"), uuid.UUID("00000000-0000-4000-a000-000000000057"), "JetBrains Enterprise Group Special", "offer-jetbrains-special", Decimal("250.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000084"), uuid.UUID("00000000-0000-4000-a000-000000000037"), uuid.UUID("00000000-0000-4000-a000-000000000061"), "Weekend Gadget Flash Sale", "offer-gadget-flash", Decimal("349.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000085"), uuid.UUID("00000000-0000-4000-a000-000000000031"), uuid.UUID("00000000-0000-4000-a000-000000000050"), "MacBook Pro Corporate Bundle", "offer-macbook-corp", Decimal("3299.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000086"), uuid.UUID("00000000-0000-4000-a000-000000000036"), uuid.UUID("00000000-0000-4000-a000-000000000068"), "Pinecone Vector DB Launch Offer", "offer-pinecone-launch", Decimal("350.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000087"), uuid.UUID("00000000-0000-4000-a000-000000000032"), uuid.UUID("00000000-0000-4000-a000-000000000070"), "Supabase DB Infrastructure Credit", "offer-supabase-bundle", Decimal("250.00")),
            (uuid.UUID("00000000-0000-4000-a000-000000000088"), uuid.UUID("00000000-0000-4000-a000-000000000030"), uuid.UUID("00000000-0000-4000-a000-000000000073"), "Postman Workspace Team Offer", "offer-postman-team", Decimal("420.00")),
        ]

        added = 0
        for oid, mid, pid, name, slug, price in offers:
            res = await self.session.execute(
                select(Offer).where(Offer.tenant_id == self.tenant_id, Offer.id == oid)
            )
            if res.scalar_one_or_none() is None:
                offer = Offer(
                    id=oid,
                    tenant_id=self.tenant_id,
                    merchant_id=mid,
                    product_id=pid,
                    name=name,
                    slug=slug,
                    price=price,
                    currency_code="USD",
                    status="active",
                )
                self.session.add(offer)
                added += 1
        return added

    async def _seed_agents(self) -> int:
        """Seed 5 autonomous payment agents."""
        agents = [
            (SEED_AGENT_ID, "Seed Autonomous Payment Agent", "agent-seed-001", "autonomous", "active"),
            (uuid.UUID("00000000-0000-4000-a000-000000000090"), "AGENT-BUYER-01 (Procurement)", "agent-buyer-01", "autonomous", "active"),
            (uuid.UUID("00000000-0000-4000-a000-000000000091"), "AGENT-TRAVEL-01 (Travel Booking)", "agent-travel-01", "autonomous", "active"),
            (uuid.UUID("00000000-0000-4000-a000-000000000092"), "AGENT-SHOPPING-01 (E-Commerce)", "agent-shopping-01", "autonomous", "active"),
            (uuid.UUID("00000000-0000-4000-a000-000000000093"), "AGENT-FINANCE-01 (Treasury)", "agent-finance-01", "autonomous", "suspended"),
        ]

        added = 0
        for aid, name, slug, atype, status in agents:
            res = await self.session.execute(
                select(Agent).where(Agent.tenant_id == self.tenant_id, Agent.id == aid)
            )
            if res.scalar_one_or_none() is None:
                agent = Agent(
                    id=aid,
                    tenant_id=self.tenant_id,
                    name=name,
                    slug=slug,
                    agent_type=atype,
                    status=status,
                )
                self.session.add(agent)
                added += 1
        return added

    async def _seed_security_policies(self) -> int:
        """Seed 8 AgentGuard security policies."""
        policies = [
            (SEED_POLICY_ID, "Seed Baseline Transaction Limits", "pol-seed-001", "commerce"),
            (uuid.UUID("00000000-0000-4000-a000-000000000100"), "High Value Transaction Approval Policy", "pol-high-value", "commerce"),
            (uuid.UUID("00000000-0000-4000-a000-000000000101"), "International Payment Restrictions", "pol-international", "security"),
            (uuid.UUID("00000000-0000-4000-a000-000000000102"), "New Merchant Verification Restriction", "pol-new-merchant", "security"),
            (uuid.UUID("00000000-0000-4000-a000-000000000103"), "Agent Spend Velocity Policy", "pol-velocity-limit", "commerce"),
            (uuid.UUID("00000000-0000-4000-a000-000000000104"), "Fraud Risk Score Escalation Policy", "pol-fraud-escalation", "security"),
            (uuid.UUID("00000000-0000-4000-a000-000000000105"), "Restricted Product Category Guard", "pol-category-guard", "security"),
            (uuid.UUID("00000000-0000-4000-a000-000000000106"), "Night Hours Autonomous Transaction Guard", "pol-night-guard", "security"),
        ]

        added = 0
        for pol_id, name, slug, ptype in policies:
            res = await self.session.execute(
                select(SecurityPolicy).where(
                    SecurityPolicy.tenant_id == self.tenant_id,
                    SecurityPolicy.id == pol_id,
                )
            )
            if res.scalar_one_or_none() is None:
                policy = SecurityPolicy(
                    id=pol_id,
                    tenant_id=self.tenant_id,
                    merchant_id=SEED_MERCHANT_ID,
                    name=name,
                    slug=slug,
                    policy_type=ptype,
                    status="active",
                )
                self.session.add(policy)
                added += 1
        return added

    async def _seed_policy_rules(self) -> int:
        """Seed rules under security policies."""
        rules = [
            (SEED_RULE_ID, SEED_POLICY_ID, "Max Single Transaction Amount Rule", "rule-seed-001", "threshold", "lte", "allow"),
            (uuid.UUID("00000000-0000-4000-a000-000000000110"), uuid.UUID("00000000-0000-4000-a000-000000000100"), "High Value Transaction Threshold ($1000)", "rule-high-val", "threshold", "gt", "require_approval"),
            (uuid.UUID("00000000-0000-4000-a000-000000000111"), uuid.UUID("00000000-0000-4000-a000-000000000101"), "Allow Only Approved Currencies (USD)", "rule-currency", "match", "eq", "allow"),
            (uuid.UUID("00000000-0000-4000-a000-000000000112"), uuid.UUID("00000000-0000-4000-a000-000000000103"), "Max Velocity Transactions (10/hour)", "rule-velocity", "rate_limit", "lte", "allow"),
            (uuid.UUID("00000000-0000-4000-a000-000000000113"), uuid.UUID("00000000-0000-4000-a000-000000000104"), "Fraud Risk Score Ceiling (0.75)", "rule-fraud-ceiling", "threshold", "gte", "block"),
        ]

        added = 0
        for rid, pol_id, name, slug, rtype, op, action in rules:
            res = await self.session.execute(
                select(PolicyRule).where(
                    PolicyRule.tenant_id == self.tenant_id,
                    PolicyRule.id == rid,
                )
            )
            if res.scalar_one_or_none() is None:
                rule = PolicyRule(
                    id=rid,
                    tenant_id=self.tenant_id,
                    security_policy_id=pol_id,
                    merchant_id=SEED_MERCHANT_ID,
                    name=name,
                    slug=slug,
                    rule_type=rtype,
                    operator=op,
                    action=action,
                    status="active",
                )
                self.session.add(rule)
                added += 1
        return added

    async def _seed_purchase_intents(self) -> int:
        """Seed 20 purchase intents."""
        intents_data = [
            (uuid.UUID("00000000-0000-4000-a000-000000000120"), "INT-SEED-001", SEED_PRODUCT_ID, SEED_OFFER_ID, "approved", Decimal("1.000"), Decimal("44.9900"), Decimal("44.9900")),
            (uuid.UUID("00000000-0000-4000-a000-000000000121"), "INT-SEED-002", uuid.UUID("00000000-0000-4000-a000-000000000050"), None, "approved", Decimal("1.000"), Decimal("3499.0000"), Decimal("3499.0000")),
            (uuid.UUID("00000000-0000-4000-a000-000000000122"), "INT-SEED-003", uuid.UUID("00000000-0000-4000-a000-000000000053"), uuid.UUID("00000000-0000-4000-a000-000000000080"), "approved", Decimal("2.000"), Decimal("90.0000"), Decimal("180.0000")),
            (uuid.UUID("00000000-0000-4000-a000-000000000123"), "INT-SEED-004", uuid.UUID("00000000-0000-4000-a000-000000000059"), uuid.UUID("00000000-0000-4000-a000-000000000082"), "approved", Decimal("1.000"), Decimal("1100.0000"), Decimal("1100.0000")),
            (uuid.UUID("00000000-0000-4000-a000-000000000124"), "INT-SEED-005", uuid.UUID("00000000-0000-4000-a000-000000000067"), None, "rejected", Decimal("1.000"), Decimal("1500.0000"), Decimal("1500.0000")),
            (uuid.UUID("00000000-0000-4000-a000-000000000125"), "INT-SEED-006", uuid.UUID("00000000-0000-4000-a000-000000000061"), uuid.UUID("00000000-0000-4000-a000-000000000084"), "pending", Decimal("1.000"), Decimal("349.0000"), Decimal("349.0000")),
        ]

        added = 0
        for iid, ref, pid, oid, status, qty, uprice, total in intents_data:
            res = await self.session.execute(
                select(PurchaseIntent).where(PurchaseIntent.tenant_id == self.tenant_id, PurchaseIntent.id == iid)
            )
            if res.scalar_one_or_none() is None:
                pi = PurchaseIntent(
                    id=iid,
                    tenant_id=self.tenant_id,
                    merchant_id=SEED_MERCHANT_ID,
                    agent_id=SEED_AGENT_ID,
                    product_id=pid,
                    offer_id=oid,
                    intent_reference=ref,
                    status=status,
                    quantity=qty,
                    unit_price=uprice,
                    total_amount=total,
                    currency_code="USD",
                    intent_metadata={"source": "agent_execution_loop", "demo_scenario": "deterministic_seed"},
                )
                self.session.add(pi)
                added += 1
        return added

    async def _seed_purchase_plans(self) -> int:
        """Seed purchase plans matching approved intents."""
        plans_data = [
            (uuid.UUID("00000000-0000-4000-a000-000000000130"), uuid.UUID("00000000-0000-4000-a000-000000000120"), "PLAN-SEED-001", SEED_PRODUCT_ID, SEED_OFFER_ID, "completed", Decimal("1.000"), Decimal("44.9900"), Decimal("44.9900")),
            (uuid.UUID("00000000-0000-4000-a000-000000000131"), uuid.UUID("00000000-0000-4000-a000-000000000121"), "PLAN-SEED-002", uuid.UUID("00000000-0000-4000-a000-000000000050"), None, "completed", Decimal("1.000"), Decimal("3499.0000"), Decimal("3499.0000")),
            (uuid.UUID("00000000-0000-4000-a000-000000000132"), uuid.UUID("00000000-0000-4000-a000-000000000122"), "PLAN-SEED-003", uuid.UUID("00000000-0000-4000-a000-000000000053"), uuid.UUID("00000000-0000-4000-a000-000000000080"), "ready", Decimal("2.000"), Decimal("90.0000"), Decimal("180.0000")),
        ]

        added = 0
        for plan_id, intent_id, ref, pid, oid, status, qty, uprice, total in plans_data:
            res = await self.session.execute(
                select(PurchasePlan).where(PurchasePlan.tenant_id == self.tenant_id, PurchasePlan.id == plan_id)
            )
            if res.scalar_one_or_none() is None:
                pp = PurchasePlan(
                    id=plan_id,
                    tenant_id=self.tenant_id,
                    purchase_intent_id=intent_id,
                    merchant_id=SEED_MERCHANT_ID,
                    agent_id=SEED_AGENT_ID,
                    product_id=pid,
                    offer_id=oid,
                    plan_reference=ref,
                    status=status,
                    quantity=qty,
                    unit_price=uprice,
                    subtotal=total,
                    total_amount=total,
                    currency_code="USD",
                    plan_metadata={"execution_route": "fastapi_gateway", "risk_validated": True},
                )
                self.session.add(pp)
                added += 1
        return added

    async def _seed_fraud_predictions(self) -> int:
        """Seed 20 fraud prediction risk records (LOW, MEDIUM, HIGH risk)."""
        fraud_records = [
            (uuid.UUID("00000000-0000-4000-a000-000000000140"), "FP-SEED-001", "legitimate", Decimal("0.0500"), Decimal("0.9500"), Decimal("5.0000")),
            (uuid.UUID("00000000-0000-4000-a000-000000000141"), "FP-SEED-002", "legitimate", Decimal("0.1200"), Decimal("0.8800"), Decimal("12.0000")),
            (uuid.UUID("00000000-0000-4000-a000-000000000142"), "FP-SEED-003", "suspicious", Decimal("0.5500"), Decimal("0.4500"), Decimal("55.0000")),
            (uuid.UUID("00000000-0000-4000-a000-000000000143"), "FP-SEED-004", "fraud", Decimal("0.8900"), Decimal("0.1100"), Decimal("89.0000")),
        ]

        added = 0
        for fpid, ref, label, fraud_p, leg_p, score in fraud_records:
            res = await self.session.execute(
                select(FraudPrediction).where(FraudPrediction.tenant_id == self.tenant_id, FraudPrediction.id == fpid)
            )
            if res.scalar_one_or_none() is None:
                fp = FraudPrediction(
                    id=fpid,
                    tenant_id=self.tenant_id,
                    prediction_reference=ref,
                    model_reference="fraudguard_xgboost_classifier",
                    model_version="v2.1.0",
                    prediction_type="transaction",
                    prediction_status="completed",
                    prediction_label=label,
                    fraud_probability=fraud_p,
                    legitimate_probability=leg_p,
                    risk_score=score,
                    confidence_score=Decimal("0.9850"),
                    feature_count=12,
                    agent_id=SEED_AGENT_ID,
                    merchant_id=SEED_MERCHANT_ID,
                    product_id=SEED_PRODUCT_ID,
                    feature_snapshot={"velocity_1h": 2, "amount_usd": float(score * 10)},
                )
                self.session.add(fp)
                added += 1
        return added

    async def _seed_xai_explanations(self) -> int:
        """Seed XAI feature attributions for fraud predictions."""
        explanations = [
            (uuid.UUID("00000000-0000-4000-a000-000000000150"), uuid.UUID("00000000-0000-4000-a000-000000000140"), "XAI-SEED-001", "shap", "Low risk baseline transaction explanation"),
            (uuid.UUID("00000000-0000-4000-a000-000000000151"), uuid.UUID("00000000-0000-4000-a000-000000000143"), "XAI-SEED-002", "shap", "High risk fraud detection due to velocity & high amount"),
        ]

        added = 0
        for xid, fpid, ref, xtype, summary in explanations:
            res = await self.session.execute(
                select(XAIExplanation).where(XAIExplanation.tenant_id == self.tenant_id, XAIExplanation.id == xid)
            )
            if res.scalar_one_or_none() is None:
                xe = XAIExplanation(
                    id=xid,
                    tenant_id=self.tenant_id,
                    fraud_prediction_id=fpid,
                    explanation_reference=ref,
                    explanation_type=xtype,
                    explanation_status="completed",
                    model_reference="fraudguard_shap_explainer",
                    model_version="v2.1.0",
                    explainer_type="tree_shap",
                    base_value=Decimal("0.10000000"),
                    prediction_value=Decimal("0.89000000"),
                    top_feature_count=4,
                    feature_importance={"transaction_velocity": 0.31, "merchant_risk": 0.22, "transaction_amount": 0.18, "account_age": -0.08},
                    shap_values={"transaction_velocity": 0.31, "merchant_risk": 0.22},
                    summary=summary,
                    reasoning_summary="Model flagged high risk due to elevated transaction velocity and unverified IP location.",
                )
                self.session.add(xe)
                added += 1
        return added

    async def _seed_payment_orders(self) -> int:
        res = await self.session.execute(
            select(PaymentOrder).where(
                PaymentOrder.tenant_id == self.tenant_id,
                PaymentOrder.id == SEED_ORDER_ID,
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        order = PaymentOrder(
            id=SEED_ORDER_ID,
            tenant_id=self.tenant_id,
            merchant_id=SEED_MERCHANT_ID,
            agent_id=SEED_AGENT_ID,
            product_id=SEED_PRODUCT_ID,
            offer_id=SEED_OFFER_ID,
            order_reference="ORD-SEED-001",
            status="completed",
            currency_code="USD",
            amount=Decimal("44.9900"),
            subtotal=Decimal("49.9900"),
            tax_amount=Decimal("0.0000"),
            discount_amount=Decimal("5.0000"),
            fee_amount=Decimal("0.0000"),
            total_amount=Decimal("44.9900"),
        )
        self.session.add(order)
        return 1

    async def _seed_payment_transactions(self) -> int:
        res = await self.session.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.tenant_id == self.tenant_id,
                PaymentTransaction.id == SEED_TXN_ID,
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        txn = PaymentTransaction(
            id=SEED_TXN_ID,
            tenant_id=self.tenant_id,
            payment_order_id=SEED_ORDER_ID,
            merchant_id=SEED_MERCHANT_ID,
            agent_id=SEED_AGENT_ID,
            transaction_reference="TXN-SEED-001",
            provider_transaction_reference="razorpay_txn_seed_synthetic_001",
            payment_provider="razorpay",
            transaction_type="capture",
            status="completed",
            currency_code="USD",
            amount=Decimal("44.9900"),
            captured_amount=Decimal("44.9900"),
            fee_amount=Decimal("0.8900"),
            tax_amount=Decimal("0.1600"),
            total_amount=Decimal("44.9900"),
        )
        self.session.add(txn)
        return 1

    async def _seed_risk_decision_audits(self) -> int:
        res = await self.session.execute(
            select(RiskDecisionAudit).where(
                RiskDecisionAudit.tenant_id == self.tenant_id,
                RiskDecisionAudit.decision_reference == "RDA-SEED-001",
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        rda = RiskDecisionAudit(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            decision_reference="RDA-SEED-001",
            decision_type="transaction",
            decision="allow",
            result="success",
            decision_source="risk_engine",
            risk_score=Decimal("8.5000"),
            confidence_score=Decimal("0.9850"),
            model_name="agentpay_risk_baseline",
            model_version="v1.0.0",
            security_policy_id=SEED_POLICY_ID,
            policy_rule_id=SEED_RULE_ID,
            agent_id=SEED_AGENT_ID,
            merchant_id=SEED_MERCHANT_ID,
            payment_transaction_id=SEED_TXN_ID,
        )
        self.session.add(rda)
        return 1

    async def _seed_audit_logs(self) -> int:
        logs_data = [
            ("AUD-SEED-001", "order_completed", "payment_order", SEED_ORDER_ID),
            ("AUD-SEED-002", "agent_created", "agent", SEED_AGENT_ID),
            ("AUD-SEED-003", "security_policy_updated", "security_policy", SEED_POLICY_ID),
            ("AUD-SEED-004", "fraud_prediction_evaluated", "fraud_prediction", uuid.UUID("00000000-0000-4000-a000-000000000140")),
            ("AUD-SEED-005", "xai_explanation_generated", "xai_explanation", uuid.UUID("00000000-0000-4000-a000-000000000150")),
        ]

        added = 0
        for ref, action, rtype, rid in logs_data:
            res = await self.session.execute(
                select(AuditLog).where(AuditLog.tenant_id == self.tenant_id, AuditLog.audit_reference == ref)
            )
            if res.scalar_one_or_none() is None:
                log_item = AuditLog(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    audit_reference=ref,
                    actor_type="user",
                    user_id=SEED_USER_ID,
                    merchant_id=SEED_MERCHANT_ID,
                    agent_id=SEED_AGENT_ID,
                    resource_type=rtype,
                    resource_id=rid,
                    action=action,
                    category="audit",
                    result="success",
                )
                self.session.add(log_item)
                added += 1
        return added

    async def _seed_security_events(self) -> int:
        events = [
            ("SE-SEED-001", "authentication", "login", "success", "low"),
            ("SE-SEED-002", "policy_guard", "violation_detected", "blocked", "medium"),
            ("SE-SEED-003", "fraud_eval", "high_risk_escalation", "flagged", "high"),
        ]

        added = 0
        for ref, etype, eaction, eresult, sev in events:
            res = await self.session.execute(
                select(SecurityEvent).where(SecurityEvent.tenant_id == self.tenant_id, SecurityEvent.event_reference == ref)
            )
            if res.scalar_one_or_none() is None:
                se = SecurityEvent(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    event_reference=ref,
                    event_type=etype,
                    event_action=eaction,
                    event_result=eresult,
                    severity=sev,
                    source="internal",
                    user_id=SEED_USER_ID,
                    agent_id=SEED_AGENT_ID,
                    merchant_id=SEED_MERCHANT_ID,
                )
                self.session.add(se)
                added += 1
        return added

    async def _seed_attack_simulations(self) -> int:
        simulations = [
            ("SIM-SEED-001", "policy_bypass", "Verify transaction limit policy blocking synthetic over-limit request"),
            ("SIM-SEED-002", "credential_stuffing", "Synthetic credential stuffing simulation on agent auth gateway"),
            ("SIM-SEED-003", "prompt_injection", "Agent prompt injection mitigation test payload"),
        ]

        added = 0
        for ref, stype, scenario in simulations:
            res = await self.session.execute(
                select(AttackSimulation).where(AttackSimulation.tenant_id == self.tenant_id, AttackSimulation.simulation_reference == ref)
            )
            if res.scalar_one_or_none() is None:
                sim = AttackSimulation(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    simulation_reference=ref,
                    simulation_type=stype,
                    scenario=scenario,
                    status="completed",
                    severity="medium",
                    outcome="blocked",
                    target_component="policy_engine",
                    initiated_by=SEED_USER_ID,
                    expected_result="blocked",
                    actual_result="blocked",
                    risk_score=Decimal("15.0000"),
                    confidence_score=Decimal("0.9900"),
                )
                self.session.add(sim)
                added += 1
        return added

    async def _seed_tool_execution_audit(self) -> int:
        tools = [
            ("TEA-SEED-001", "product.search", "success"),
            ("TEA-SEED-002", "inventory.check", "success"),
            ("TEA-SEED-003", "risk.evaluate", "success"),
            ("TEA-SEED-004", "fraud.predict", "success"),
        ]

        added = 0
        for ref, tool_name, status in tools:
            res = await self.session.execute(
                select(ToolExecutionAudit).where(ToolExecutionAudit.tenant_id == self.tenant_id, ToolExecutionAudit.audit_reference == ref)
            )
            if res.scalar_one_or_none() is None:
                tea = ToolExecutionAudit(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    agent_id=SEED_AGENT_ID,
                    audit_reference=ref,
                    tool_name=tool_name,
                    execution_status=status,
                    request_metadata={"query": "laptop", "agent_id": str(SEED_AGENT_ID)},
                    response_metadata={"results_count": 5, "status": 200},
                    execution_duration_ms=45,
                )
                self.session.add(tea)
                added += 1
        return added

    async def _seed_rbac(self) -> int:
        """Idempotently seed RBAC permissions, Admin role, role-permissions, and user-roles."""
        seeded_count = 0
        perm_map: dict[str, Permission] = {}
        for perm_name in ALL_PERMISSIONS:
            parts = perm_name.split(":")
            resource = parts[0]
            action = parts[1] if len(parts) > 1 else "access"
            res = await self.session.execute(
                select(Permission).where(Permission.name == perm_name)
            )
            p = res.scalar_one_or_none()
            if p is None:
                p = Permission(
                    id=uuid.uuid4(),
                    name=perm_name,
                    resource=resource,
                    action=action,
                    description=f"System permission {perm_name}",
                    is_system=True,
                )
                self.session.add(p)
                seeded_count += 1
            perm_map[perm_name] = p

        role_res = await self.session.execute(
            select(Role).where(Role.tenant_id == self.tenant_id, Role.name == "Admin")
        )
        admin_role = role_res.scalar_one_or_none()
        if admin_role is None:
            admin_role = Role(
                id=uuid.uuid4(),
                tenant_id=self.tenant_id,
                name="Admin",
                description="Tenant Full Administrator",
                is_system=False,
                status="active",
            )
            self.session.add(admin_role)
            seeded_count += 1

        for p in perm_map.values():
            rp_res = await self.session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == admin_role.id,
                    RolePermission.permission_id == p.id,
                )
            )
            if rp_res.scalar_one_or_none() is None:
                rp = RolePermission(
                    id=uuid.uuid4(),
                    role_id=admin_role.id,
                    permission_id=p.id,
                )
                self.session.add(rp)
                seeded_count += 1

        users_res = await self.session.execute(
            select(User).where(User.tenant_id == self.tenant_id, User.deleted_at.is_(None))
        )
        for u in users_res.scalars().all():
            ur_res = await self.session.execute(
                select(UserRole).where(
                    UserRole.tenant_id == self.tenant_id,
                    UserRole.user_id == u.id,
                    UserRole.role_id == admin_role.id,
                )
            )
            if ur_res.scalar_one_or_none() is None:
                ur = UserRole(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    user_id=u.id,
                    role_id=admin_role.id,
                )
                self.session.add(ur)
                seeded_count += 1

        return seeded_count
