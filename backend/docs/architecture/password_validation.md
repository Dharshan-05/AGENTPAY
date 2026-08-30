# AGENTPAY Architecture — Password Validation (Phase 108)

## Overview
Password validation in AGENTPAY formalizes password strength policy enforcement across user registration and credential operations.

## Key Design Principles & Policy Requirements
1. **Centralized Policy Enforcement**: Implemented in `app/core/security.py` (`validate_password_strength`).
2. **Policy Criteria**:
   - Minimum length: 8 characters
   - Maximum length: 128 characters
   - Complexity: at least one uppercase letter, one lowercase letter, one numerical digit, and one special character.
3. **Separation of Concerns**: Password validation evaluates policy compliance before password hashing is invoked.
4. **Unicode & Whitespace Handling**: Properly handles Unicode strings without exposing internal regex patterns or database errors.
5. **Standardized Error Handling**: Violations raise `PasswordPolicyError`, mapping cleanly to HTTP 400 Bad Request responses.
