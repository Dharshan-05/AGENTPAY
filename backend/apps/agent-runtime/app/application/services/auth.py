"""Authentication application service module for AGENTPAY (Phase 101–106)."""

import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.jwt import create_access_token
from app.core.security import hash_password, validate_password_strength, verify_password
from app.core.tokens import generate_opaque_token, hash_token
from app.domain.exceptions.auth_exceptions import (
    AccountDisabledError,
    AccountLockedError,
    AuthenticationFailedError,
    UserAlreadyExistsError,
)
from app.infrastructure.database.models.authentication_security import AuthenticationSecurity
from app.infrastructure.database.models.login_security_event import LoginSecurityEvent
from app.infrastructure.database.models.refresh_token import RefreshToken
from app.infrastructure.database.models.session import Session as SessionModel
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.user_profile import UserProfile
from app.schemas.auth import (
    TokenRefreshRequest,
    TokenRefreshResponseData,
    UserLoginRequest,
    UserLoginResponseData,
    UserProfileResponse,
    UserRegisterRequest,
    UserRegisterResponseData,
)

logger = logging.getLogger("agentpay.auth.service")

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
SESSION_DURATION_DAYS = 1
REFRESH_TOKEN_DURATION_DAYS = 7


class AuthenticationService:
    """Application service for User Authentication, Registration, Login, JWT, & Tokens."""

    async def register_user(
        self,
        db: AsyncSession,
        request_data: UserRegisterRequest,
        request_id: str | None = None,
    ) -> UserRegisterResponseData:
        """Execute production-grade user registration with tenant isolation and security events."""
        normalized_email = request_data.email.strip().lower()

        # 1. Enforce tenant isolation and uniqueness
        existing_stmt = select(User).where(
            User.tenant_id == request_data.tenant_id,
            User.email == normalized_email,
            User.deleted_at.is_(None),
        )
        existing_result = await db.execute(existing_stmt)
        if existing_result.scalar_one_or_none() is not None:
            logger.warning(
                "Registration attempt with existing email in tenant: %s",
                normalized_email,
                extra={"tenant_id": str(request_data.tenant_id), "request_id": request_id},
            )
            raise UserAlreadyExistsError()

        # 2. Validate password strength policy
        validate_password_strength(request_data.password)

        # 3. Hash password securely (zero plaintext password persistence)
        pwd_hash = hash_password(request_data.password)

        # 4. Construct user entity
        user = User(
            id=uuid.uuid4(),
            tenant_id=request_data.tenant_id,
            email=normalized_email,
            password_hash=pwd_hash,
            status="active",
            created_at=datetime.now(UTC),
        )

        # 5. Construct profile entity
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            tenant_id=request_data.tenant_id,
            first_name=request_data.first_name,
            last_name=request_data.last_name,
            display_name=request_data.display_name,
        )

        # 6. Construct authentication security state tracking entity
        auth_sec = AuthenticationSecurity(
            id=uuid.uuid4(),
            user_id=user.id,
            tenant_id=request_data.tenant_id,
            failed_login_attempts=0,
            status="active",
        )

        # 7. Construct security audit event
        audit_event = LoginSecurityEvent(
            id=uuid.uuid4(),
            tenant_id=request_data.tenant_id,
            user_id=user.id,
            event_type="user_registered",
            event_result="success",
            request_id=request_id,
            event_metadata={"email": normalized_email},
        )

        # 8. Persist atomically
        db.add_all([user, profile, auth_sec, audit_event])
        await db.commit()
        await db.refresh(user)
        await db.refresh(profile)

        profile_resp = UserProfileResponse(
            id=profile.id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            display_name=profile.display_name,
        )

        return UserRegisterResponseData(
            user_id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            status=user.status,
            created_at=user.created_at,
            profile=profile_resp,
        )

    async def authenticate_user(
        self,
        db: AsyncSession,
        request_data: UserLoginRequest,
        request_id: str | None = None,
    ) -> UserLoginResponseData:
        """Execute user authentication, session creation, and token issuance."""

        normalized_email = request_data.email.strip().lower()
        now = datetime.now(UTC)

        # 1. Tenant-scoped user lookup
        stmt = (
            select(User)
            .where(
                User.tenant_id == request_data.tenant_id,
                User.email == normalized_email,
                User.deleted_at.is_(None),
            )
            .options(selectinload(User.profile))
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            sec_event = LoginSecurityEvent(
                id=uuid.uuid4(),
                tenant_id=request_data.tenant_id,
                user_id=None,
                event_type="login_failed",
                event_result="failure",
                ip_address=request_data.ip_address,
                user_agent=request_data.user_agent,
                request_id=request_id,
                event_metadata={"reason": "user_not_found"},
            )
            db.add(sec_event)
            await db.commit()

            raise AuthenticationFailedError()

        # 2. Check account status
        if user.status.lower() in ("suspended", "disabled", "inactive"):
            sec_event = LoginSecurityEvent(
                id=uuid.uuid4(),
                tenant_id=request_data.tenant_id,
                user_id=user.id,
                event_type="login_rejected",
                event_result="failure",
                ip_address=request_data.ip_address,
                user_agent=request_data.user_agent,
                request_id=request_id,
                event_metadata={"reason": f"account_{user.status}"},
            )
            db.add(sec_event)
            await db.commit()

            raise AccountDisabledError()

        # 3. Retrieve or create authentication security tracking entity
        sec_stmt = select(AuthenticationSecurity).where(
            AuthenticationSecurity.user_id == user.id,
            AuthenticationSecurity.tenant_id == request_data.tenant_id,
        )
        sec_result = await db.execute(sec_stmt)
        auth_sec = sec_result.scalar_one_or_none()

        if auth_sec is None:
            auth_sec = AuthenticationSecurity(
                id=uuid.uuid4(),
                user_id=user.id,
                tenant_id=request_data.tenant_id,
                failed_login_attempts=0,
                status="active",
            )
            db.add(auth_sec)
            await db.flush()

        # 4. Check lockout status
        if auth_sec.status.lower() == "locked" or (
            auth_sec.locked_until is not None and now < auth_sec.locked_until
        ):
            sec_event = LoginSecurityEvent(
                id=uuid.uuid4(),
                tenant_id=request_data.tenant_id,
                user_id=user.id,
                event_type="login_rejected",
                event_result="failure",
                ip_address=request_data.ip_address,
                user_agent=request_data.user_agent,
                request_id=request_id,
                event_metadata={"reason": "account_locked"},
            )
            db.add(sec_event)
            await db.commit()

            raise AccountLockedError()

        # 5. Verify password securely
        is_valid = verify_password(request_data.password, user.password_hash or "")

        if not is_valid:
            auth_sec.failed_login_attempts += 1
            auth_sec.last_failed_login_at = now

            if auth_sec.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                auth_sec.status = "locked"
                auth_sec.locked_at = now
                auth_sec.locked_until = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                user.status = "locked"
                user.locked_until = auth_sec.locked_until

                lock_event = LoginSecurityEvent(
                    id=uuid.uuid4(),
                    tenant_id=request_data.tenant_id,
                    user_id=user.id,
                    event_type="account_locked",
                    event_result="failure",
                    ip_address=request_data.ip_address,
                    user_agent=request_data.user_agent,
                    request_id=request_id,
                    event_metadata={"failed_attempts": auth_sec.failed_login_attempts},
                )
                db.add(lock_event)

            fail_event = LoginSecurityEvent(
                id=uuid.uuid4(),
                tenant_id=request_data.tenant_id,
                user_id=user.id,
                event_type="login_failed",
                event_result="failure",
                ip_address=request_data.ip_address,
                user_agent=request_data.user_agent,
                request_id=request_id,
                event_metadata={"failed_attempts": auth_sec.failed_login_attempts},
            )
            db.add(fail_event)
            await db.commit()

            raise AuthenticationFailedError()

        # 6. Password verified — reset failure counters & update activity timestamps
        auth_sec.failed_login_attempts = 0
        auth_sec.status = "active"
        auth_sec.locked_until = None
        auth_sec.last_successful_login_at = now
        user.last_login_at = now

        # 7. Create authenticated session entity
        expires_at = now + timedelta(days=SESSION_DURATION_DAYS)
        session_obj = SessionModel(
            id=uuid.uuid4(),
            tenant_id=request_data.tenant_id,
            user_id=user.id,
            status="active",
            device_id=request_data.device_id,
            user_agent=request_data.user_agent,
            ip_address=request_data.ip_address,
            last_activity_at=now,
            expires_at=expires_at,
        )

        # 8. Issue signed JWT access token and opaque refresh token
        access_token = create_access_token(
            tenant_id=request_data.tenant_id,
            user_id=user.id,
            session_id=session_obj.id,
        )

        raw_refresh_token = generate_opaque_token()
        refresh_token_digest = hash_token(raw_refresh_token)
        refresh_expires_at = now + timedelta(days=REFRESH_TOKEN_DURATION_DAYS)

        family_id = uuid.uuid4()
        refresh_token_obj = RefreshToken(
            id=uuid.uuid4(),
            tenant_id=request_data.tenant_id,
            session_id=session_obj.id,
            token_hash=refresh_token_digest,
            family_id=family_id,
            parent_token_id=None,
            status="active",
            expires_at=refresh_expires_at,
        )

        # 9. Record successful login security event
        success_event = LoginSecurityEvent(
            id=uuid.uuid4(),
            tenant_id=request_data.tenant_id,
            user_id=user.id,
            session_id=session_obj.id,
            refresh_token_id=refresh_token_obj.id,
            event_type="login_success",
            event_result="success",
            ip_address=request_data.ip_address,
            user_agent=request_data.user_agent,
            request_id=request_id,
            event_metadata={},
        )

        db.add_all([session_obj, refresh_token_obj, success_event])
        await db.commit()

        return UserLoginResponseData(
            user_id=user.id,
            tenant_id=user.tenant_id,
            session_id=session_obj.id,
            email=user.email,
            status=user.status,
            expires_at=expires_at,
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="Bearer",
        )

    async def refresh_tokens(
        self,
        db: AsyncSession,
        request_data: TokenRefreshRequest,
        request_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenRefreshResponseData:
        """Execute refresh token verification, rotation, replay detection, & token issuance."""

        raw_token = request_data.refresh_token.strip()
        target_digest = hash_token(raw_token)
        now = datetime.now(UTC)

        # 1. Lookup refresh token in tenant scope
        token_stmt = (
            select(RefreshToken)
            .where(
                RefreshToken.tenant_id == request_data.tenant_id,
                RefreshToken.token_hash == target_digest,
            )
            .options(selectinload(RefreshToken.session))
        )
        result = await db.execute(token_stmt)
        token_record = result.scalar_one_or_none()

        if token_record is None:
            sec_event = LoginSecurityEvent(
                id=uuid.uuid4(),
                tenant_id=request_data.tenant_id,
                user_id=None,
                event_type="refresh_failed",
                event_result="failure",
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                event_metadata={"reason": "token_not_found"},
            )
            db.add(sec_event)
            await db.commit()
            raise AuthenticationFailedError("Invalid refresh token.")

        # 2. Replay Detection Check: token was already rotated!
        if token_record.status.lower() == "rotated":
            # REPLAY DETECTED: Revoke entire token family and session!
            family_id = token_record.family_id or token_record.id
            token_record.reuse_detected_at = now

            # Revoke all tokens in family
            fam_stmt = select(RefreshToken).where(
                RefreshToken.tenant_id == request_data.tenant_id,
                RefreshToken.family_id == family_id,
            )
            fam_res = await db.execute(fam_stmt)
            for tok in fam_res.scalars():
                tok.status = "revoked"
                tok.revoked_at = now

            # Revoke session
            session_obj = token_record.session
            if session_obj is not None:
                session_obj.status = "revoked"
                session_obj.revocation_reason = "refresh_token_reuse_detected"
                session_obj.revoked_at = now

            replay_event = LoginSecurityEvent(
                id=uuid.uuid4(),
                tenant_id=request_data.tenant_id,
                user_id=session_obj.user_id if session_obj else None,
                session_id=session_obj.id if session_obj else None,
                refresh_token_id=token_record.id,
                event_type="refresh_reuse_detected",
                event_result="failure",
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                event_metadata={"family_id": str(family_id)},
            )
            db.add(replay_event)
            await db.commit()

            raise AuthenticationFailedError("Security violation: Refresh token reuse detected.")

        if token_record.status.lower() == "revoked":
            sec_event = LoginSecurityEvent(
                id=uuid.uuid4(),
                tenant_id=request_data.tenant_id,
                user_id=token_record.session.user_id if token_record.session else None,
                event_type="refresh_failed",
                event_result="failure",
                request_id=request_id,
                event_metadata={"reason": "token_revoked"},
            )
            db.add(sec_event)
            await db.commit()
            raise AuthenticationFailedError("Refresh token is revoked.")

        # 3. Expiration Check
        if token_record.expires_at is not None and now > token_record.expires_at:
            token_record.status = "expired"
            sec_event = LoginSecurityEvent(
                id=uuid.uuid4(),
                tenant_id=request_data.tenant_id,
                user_id=token_record.session.user_id if token_record.session else None,
                event_type="refresh_expired",
                event_result="failure",
                request_id=request_id,
            )
            db.add(sec_event)
            await db.commit()
            raise AuthenticationFailedError("Refresh token expired.")

        # 4. Session State Check
        session_obj = token_record.session
        if (
            session_obj is None
            or session_obj.status.lower() != "active"
            or (session_obj.expires_at is not None and now > session_obj.expires_at)
        ):
            token_record.status = "revoked"
            sec_event = LoginSecurityEvent(
                id=uuid.uuid4(),
                tenant_id=request_data.tenant_id,
                user_id=session_obj.user_id if session_obj else None,
                event_type="refresh_failed",
                event_result="failure",
                request_id=request_id,
                event_metadata={"reason": "session_inactive"},
            )
            db.add(sec_event)
            await db.commit()
            raise AuthenticationFailedError("Session expired or revoked.")

        # 5. User Account Status Check
        user_stmt = select(User).where(
            User.id == session_obj.user_id,
            User.tenant_id == request_data.tenant_id,
            User.deleted_at.is_(None),
        )
        user_res = await db.execute(user_stmt)
        user_obj = user_res.scalar_one_or_none()

        if user_obj is None or user_obj.status.lower() in (
            "suspended",
            "disabled",
            "inactive",
            "locked",
        ):
            token_record.status = "revoked"
            sec_event = LoginSecurityEvent(
                id=uuid.uuid4(),
                tenant_id=request_data.tenant_id,
                user_id=session_obj.user_id,
                event_type="refresh_failed",
                event_result="failure",
                request_id=request_id,
                event_metadata={"reason": "user_disabled"},
            )
            db.add(sec_event)
            await db.commit()
            raise AccountDisabledError("User account is disabled or suspended.")

        # 6. Execute Rotation
        token_record.status = "rotated"
        token_record.rotated_at = now

        new_raw_refresh_token = generate_opaque_token()
        new_digest = hash_token(new_raw_refresh_token)
        new_expires_at = now + timedelta(days=REFRESH_TOKEN_DURATION_DAYS)

        new_token_record = RefreshToken(
            id=uuid.uuid4(),
            tenant_id=request_data.tenant_id,
            session_id=session_obj.id,
            token_hash=new_digest,
            family_id=token_record.family_id or token_record.id,
            parent_token_id=token_record.id,
            status="active",
            expires_at=new_expires_at,
        )

        new_access_token = create_access_token(
            tenant_id=request_data.tenant_id,
            user_id=user_obj.id,
            session_id=session_obj.id,
        )

        session_obj.last_activity_at = now

        refresh_success_event = LoginSecurityEvent(
            id=uuid.uuid4(),
            tenant_id=request_data.tenant_id,
            user_id=user_obj.id,
            session_id=session_obj.id,
            refresh_token_id=new_token_record.id,
            event_type="refresh_success",
            event_result="success",
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )

        db.add_all([new_token_record, refresh_success_event])
        await db.commit()

        return TokenRefreshResponseData(
            access_token=new_access_token,
            refresh_token=new_raw_refresh_token,
            token_type="Bearer",
            expires_at=new_expires_at,
        )

    async def logout_user(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        request_id: str | None = None,
    ) -> None:
        """Revoke active user session and associated refresh tokens on logout."""
        now = datetime.now(UTC)

        # 1. Revoke session
        session_stmt = select(SessionModel).where(
            SessionModel.id == session_id,
            SessionModel.tenant_id == tenant_id,
            SessionModel.user_id == user_id,
        )
        session_res = await db.execute(session_stmt)
        session_obj = session_res.scalar_one_or_none()

        if session_obj is not None:
            session_obj.status = "revoked"
            session_obj.revoked_at = now
            session_obj.revocation_reason = "user_logout"

        # 2. Revoke all refresh tokens for session
        tokens_stmt = select(RefreshToken).where(
            RefreshToken.tenant_id == tenant_id,
            RefreshToken.session_id == session_id,
        )
        tokens_res = await db.execute(tokens_stmt)
        for tok in tokens_res.scalars():
            tok.status = "revoked"
            tok.revoked_at = now

        # 3. Record logout security event
        logout_event = LoginSecurityEvent(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session_id,
            event_type="logout_success",
            event_result="success",
            request_id=request_id,
        )

        db.add(logout_event)
        await db.commit()

    async def logout_all_sessions(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        request_id: str | None = None,
    ) -> None:
        """Revoke ALL active user sessions and associated refresh tokens within tenant scope."""
        now = datetime.now(UTC)

        # 1. Fetch active sessions for user in tenant
        sessions_stmt = select(SessionModel).where(
            SessionModel.tenant_id == tenant_id,
            SessionModel.user_id == user_id,
        )
        sessions_res = await db.execute(sessions_stmt)
        active_sessions = list(sessions_res.scalars())

        session_ids = [s.id for s in active_sessions]
        for session_obj in active_sessions:
            session_obj.status = "revoked"
            session_obj.revoked_at = now
            session_obj.revocation_reason = "user_logout_all"

        # 2. Revoke all refresh tokens for these sessions
        if session_ids:
            tokens_stmt = select(RefreshToken).where(
                RefreshToken.tenant_id == tenant_id,
                RefreshToken.session_id.in_(session_ids),
            )
            tokens_res = await db.execute(tokens_stmt)
            for tok in tokens_res.scalars():
                tok.status = "revoked"
                tok.revoked_at = now

        # 3. Record security audit event
        logout_event = LoginSecurityEvent(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            event_type="logout_all_success",
            event_result="success",
            request_id=request_id,
            event_metadata={"revoked_sessions_count": len(active_sessions)},
        )

        db.add(logout_event)
        await db.commit()
