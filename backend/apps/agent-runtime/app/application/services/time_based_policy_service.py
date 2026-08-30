"""Time-Based Policy Eligibility Evaluation Service for AGENTPAY (Phase 194)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.schemas.time_based_policies import (
    TimeBasedPolicyEvaluationRequest,
    TimeBasedPolicyEvaluationResult,
)

logger = logging.getLogger("agentguard.security.time_based_policy_service")


class TimeBasedPolicyService:
    """Production Time-Based Policy Eligibility Evaluation Engine (Phase 194 - Read/Decision Only)."""  # noqa: E501

    def evaluate_time_eligibility(
        self,
        request: TimeBasedPolicyEvaluationRequest,
    ) -> TimeBasedPolicyEvaluationResult:
        """Evaluate policy time constraints against evaluation timestamp fail-closed (Phase 194)."""
        now = datetime.now(UTC)

        # 1. Resolve Timezone safely using ZoneInfo
        tz_name = request.timezone or "UTC"
        try:
            tz = ZoneInfo(tz_name)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            logger.warning("Invalid timezone '%s' specified in policy evaluation: %s", tz_name, exc)
            return TimeBasedPolicyEvaluationResult(
                is_eligible=False,
                window_type="INVALID",
                reason_code="INVALID_TIMEZONE",
                explanation=f"Invalid or unrecognized IANA timezone '{tz_name}'.",
                evaluated_at=now,
            )

        # 2. Convert evaluation timestamp to local timezone
        eval_utc = request.evaluation_time
        if eval_utc.tzinfo is None:
            eval_utc = eval_utc.replace(tzinfo=UTC)
        local_eval = eval_utc.astimezone(tz)

        # 3. Date Range Check (starts_at & ends_at)
        if request.starts_at is not None:
            starts_utc = (
                request.starts_at.replace(tzinfo=UTC)
                if request.starts_at.tzinfo is None
                else request.starts_at
            )
            if eval_utc < starts_utc:
                return TimeBasedPolicyEvaluationResult(
                    is_eligible=False,
                    window_type="DATE_RANGE",
                    reason_code="OUTSIDE_EFFECTIVE_WINDOW",
                    explanation=f"Evaluation time ({eval_utc.isoformat()}) is before policy effective start date ({starts_utc.isoformat()}).",  # noqa: E501
                    evaluated_at=now,
                )

        if request.ends_at is not None:
            ends_utc = (
                request.ends_at.replace(tzinfo=UTC)
                if request.ends_at.tzinfo is None
                else request.ends_at
            )
            if eval_utc >= ends_utc:
                return TimeBasedPolicyEvaluationResult(
                    is_eligible=False,
                    window_type="DATE_RANGE",
                    reason_code="POLICY_EXPIRED",
                    explanation=f"Policy effective date expired at {ends_utc.isoformat()}.",
                    evaluated_at=now,
                )

        # 4. Day of Week Check
        has_day_restriction = bool(request.allowed_days)
        if has_day_restriction:
            norm_days = [d.strip().lower() for d in request.allowed_days if d.strip()]
            current_day_name = local_eval.strftime("%A").lower()
            current_day_num = str(local_eval.weekday())

            if current_day_name not in norm_days and current_day_num not in norm_days:
                return TimeBasedPolicyEvaluationResult(
                    is_eligible=False,
                    window_type="DAY_OF_WEEK",
                    reason_code="OUTSIDE_ALLOWED_DAY",
                    explanation=f"Current day '{current_day_name}' is not in policy allowed days ({request.allowed_days}).",  # noqa: E501
                    evaluated_at=now,
                )

        # 5. Time Window Check (HH:MM with Midnight Crossing support)
        has_time_window = bool(request.time_window_start and request.time_window_end)
        if has_time_window:
            try:
                t_start = time.fromisoformat(request.time_window_start.strip())  # type: ignore[union-attr]  # noqa: E501
                t_end = time.fromisoformat(request.time_window_end.strip())  # type: ignore[union-attr]  # noqa: E501
            except ValueError as exc:
                logger.warning("Invalid time window format in policy: %s", exc)
                return TimeBasedPolicyEvaluationResult(
                    is_eligible=False,
                    window_type="TIME_WINDOW",
                    reason_code="INVALID_TIME_CONFIGURATION",
                    explanation="Invalid time window format. Expected HH:MM.",
                    evaluated_at=now,
                )

            current_time = local_eval.time()

            # Check window (handling midnight crossing e.g. 22:00 -> 06:00)
            if t_start <= t_end:
                in_window = t_start <= current_time <= t_end
            else:
                in_window = current_time >= t_start or current_time <= t_end

            if not in_window:
                return TimeBasedPolicyEvaluationResult(
                    is_eligible=False,
                    window_type="TIME_WINDOW",
                    reason_code="OUTSIDE_TIME_WINDOW",
                    explanation=f"Current time ({current_time.strftime('%H:%M')}) is outside allowed time window ({request.time_window_start} - {request.time_window_end}).",  # noqa: E501
                    evaluated_at=now,
                )

        # 6. Determine Window Type Classification
        if (request.starts_at or request.ends_at) and has_time_window:
            window_type = "DATE_AND_TIME_WINDOW"
        elif has_time_window:
            window_type = "TIME_WINDOW"
        elif has_day_restriction:
            window_type = "DAY_OF_WEEK"
        elif request.starts_at or request.ends_at:
            window_type = "DATE_RANGE"
        else:
            window_type = "ALWAYS_ACTIVE"

        return TimeBasedPolicyEvaluationResult(
            is_eligible=True,
            window_type=window_type,
            reason_code="TIME_POLICY_ACTIVE",
            explanation="Policy is currently within effective time bounds.",
            evaluated_at=now,
        )
