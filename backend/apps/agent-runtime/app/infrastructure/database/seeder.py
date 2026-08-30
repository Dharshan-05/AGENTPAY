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
        counts["merchants"] = await self._seed_merchants()
        counts["agents"] = await self._seed_agents()
        counts["product_categories"] = await self._seed_product_categories()
        counts["products"] = await self._seed_products()
        counts["offers"] = await self._seed_offers()
        counts["inventory"] = await self._seed_inventory()
        counts["security_policies"] = await self._seed_security_policies()
        counts["policy_rules"] = await self._seed_policy_rules()
        counts["payment_orders"] = await self._seed_payment_orders()
        counts["payment_transactions"] = await self._seed_payment_transactions()
        counts["audit_logs"] = await self._seed_audit_logs()
        counts["security_events"] = await self._seed_security_events()
        counts["attack_simulations"] = await self._seed_attack_simulations()
        counts["rbac"] = await self._seed_rbac()

        await self.session.commit()
        return counts

    async def _seed_users(self) -> int:
        res = await self.session.execute(
            select(User).where(User.tenant_id == self.tenant_id, User.id == SEED_USER_ID)
        )
        if res.scalar_one_or_none() is not None:
            return 0

        user = User(
            id=SEED_USER_ID,
            tenant_id=self.tenant_id,
            email="seed.reviewer@agentpay.internal",
            password_hash="$argon2id$v=19$m=65536,t=3,p=4$synthetic_seed_hash",
            status="active",
        )
        profile = UserProfile(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            user_id=SEED_USER_ID,
            first_name="Seed System",
            last_name="Reviewer",
            display_name="Seed System Reviewer",
        )
        self.session.add(user)
        self.session.add(profile)
        return 1

    async def _seed_merchants(self) -> int:
        res = await self.session.execute(
            select(Merchant).where(
                Merchant.tenant_id == self.tenant_id,
                Merchant.id == SEED_MERCHANT_ID,
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        merchant = Merchant(
            id=SEED_MERCHANT_ID,
            tenant_id=self.tenant_id,
            name="Seed Commerce Merchant",
            slug="merch-seed-001",
            status="active",
        )
        self.session.add(merchant)
        return 1

    async def _seed_agents(self) -> int:
        res = await self.session.execute(
            select(Agent).where(Agent.tenant_id == self.tenant_id, Agent.id == SEED_AGENT_ID)
        )
        if res.scalar_one_or_none() is not None:
            return 0

        agent = Agent(
            id=SEED_AGENT_ID,
            tenant_id=self.tenant_id,
            name="Seed Autonomous Payment Agent",
            slug="agent-seed-001",
            agent_type="autonomous",
            status="active",
        )
        self.session.add(agent)
        return 1

    async def _seed_product_categories(self) -> int:
        res = await self.session.execute(
            select(ProductCategory).where(
                ProductCategory.tenant_id == self.tenant_id,
                ProductCategory.id == SEED_CATEGORY_ID,
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        cat = ProductCategory(
            id=SEED_CATEGORY_ID,
            tenant_id=self.tenant_id,
            merchant_id=SEED_MERCHANT_ID,
            name="Seed Software Services",
            slug="cat-seed-001",
            status="active",
        )
        self.session.add(cat)
        return 1

    async def _seed_products(self) -> int:
        res = await self.session.execute(
            select(Product).where(
                Product.tenant_id == self.tenant_id,
                Product.id == SEED_PRODUCT_ID,
            )
        )

        if res.scalar_one_or_none() is not None:
            return 0

        prod = Product(
            id=SEED_PRODUCT_ID,
            tenant_id=self.tenant_id,
            merchant_id=SEED_MERCHANT_ID,
            name="Seed Agent Execution Token Pass",
            sku="PROD-SEED-001",
            price=Decimal("49.99"),
            currency_code="USD",
            status="active",
        )
        self.session.add(prod)
        return 1

    async def _seed_offers(self) -> int:
        res = await self.session.execute(
            select(Offer).where(Offer.tenant_id == self.tenant_id, Offer.id == SEED_OFFER_ID)
        )
        if res.scalar_one_or_none() is not None:
            return 0

        offer = Offer(
            id=SEED_OFFER_ID,
            tenant_id=self.tenant_id,
            merchant_id=SEED_MERCHANT_ID,
            product_id=SEED_PRODUCT_ID,
            name="Seed Agent Runtime Trial Discount",
            slug="offer-seed-001",
            price=Decimal("44.99"),
            currency_code="USD",
            status="active",
        )
        self.session.add(offer)
        return 1

    async def _seed_inventory(self) -> int:
        res = await self.session.execute(
            select(Inventory).where(
                Inventory.tenant_id == self.tenant_id,
                Inventory.product_id == SEED_PRODUCT_ID,
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        inv = Inventory(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            merchant_id=SEED_MERCHANT_ID,
            product_id=SEED_PRODUCT_ID,
            quantity=1000,
            reserved_quantity=0,
            available_quantity=1000,
            reorder_level=10,
            status="active",
        )
        self.session.add(inv)
        return 1

    async def _seed_security_policies(self) -> int:
        res = await self.session.execute(
            select(SecurityPolicy).where(
                SecurityPolicy.tenant_id == self.tenant_id,
                SecurityPolicy.id == SEED_POLICY_ID,
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        policy = SecurityPolicy(
            id=SEED_POLICY_ID,
            tenant_id=self.tenant_id,
            merchant_id=SEED_MERCHANT_ID,
            name="Seed Baseline Transaction Limits",
            slug="pol-seed-001",
            policy_type="commerce",
            status="active",
        )
        self.session.add(policy)
        return 1

    async def _seed_policy_rules(self) -> int:
        res = await self.session.execute(
            select(PolicyRule).where(
                PolicyRule.tenant_id == self.tenant_id,
                PolicyRule.id == SEED_RULE_ID,
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        rule = PolicyRule(
            id=SEED_RULE_ID,
            tenant_id=self.tenant_id,
            security_policy_id=SEED_POLICY_ID,
            merchant_id=SEED_MERCHANT_ID,
            name="Max Single Transaction Amount Rule",
            slug="rule-seed-001",
            rule_type="threshold",
            operator="lte",
            action="allow",
            status="active",
        )
        self.session.add(rule)
        return 1

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

    async def _seed_audit_logs(self) -> int:
        res = await self.session.execute(
            select(AuditLog).where(
                AuditLog.tenant_id == self.tenant_id,
                AuditLog.audit_reference == "AUD-SEED-001",
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        log_item = AuditLog(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            audit_reference="AUD-SEED-001",
            actor_type="user",
            user_id=SEED_USER_ID,
            merchant_id=SEED_MERCHANT_ID,
            agent_id=SEED_AGENT_ID,
            resource_type="payment_order",
            resource_id=SEED_ORDER_ID,
            action="order_completed",
            category="payment",
            result="success",
        )
        self.session.add(log_item)
        return 1

    async def _seed_security_events(self) -> int:
        res = await self.session.execute(
            select(SecurityEvent).where(
                SecurityEvent.tenant_id == self.tenant_id,
                SecurityEvent.event_reference == "SE-SEED-001",
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        se = SecurityEvent(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            event_reference="SE-SEED-001",
            event_type="authentication",
            event_action="login",
            event_result="success",
            severity="low",
            source="internal",
            user_id=SEED_USER_ID,
            agent_id=SEED_AGENT_ID,
            merchant_id=SEED_MERCHANT_ID,
        )
        self.session.add(se)
        return 1

    async def _seed_attack_simulations(self) -> int:
        res = await self.session.execute(
            select(AttackSimulation).where(
                AttackSimulation.tenant_id == self.tenant_id,
                AttackSimulation.simulation_reference == "SIM-SEED-001",
            )
        )
        if res.scalar_one_or_none() is not None:
            return 0

        sim = AttackSimulation(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            simulation_reference="SIM-SEED-001",
            simulation_type="policy_bypass",
            scenario="Verify transaction limit policy blocking synthetic over-limit request",
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
