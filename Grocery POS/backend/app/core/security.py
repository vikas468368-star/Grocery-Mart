"""Security and JWT token management for Grocery Store POS."""
import bcrypt
import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    )
except ModuleNotFoundError:  # pragma: no cover - only used in minimal local installs
    PasswordHasher = None
    VerifyMismatchError = VerificationError = InvalidHashError = ValueError

from app.core.config import settings


# Argon2id password hashing configuration
password_hasher = (
    PasswordHasher(
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
    )
    if PasswordHasher is not None
    else None
)


def generate_invoice_number() -> str:
    """Generate a human-readable invoice identifier."""
    token = secrets.token_hex(3).upper()
    return f"INV-{token}"


def get_password_hash(password: str) -> str:
    """Generate a secure Argon2id password hash."""
    if not password:
        raise ValueError("Password cannot be empty.")

    if password_hasher is not None:
        return password_hasher.hash(password)
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def hash_secret(value: str) -> str:
    """Compatibility wrapper for existing seed code."""
    return get_password_hash(value)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify Argon2id or legacy SHA-256 password hashes."""

    if not plain_password or not hashed_password:
        return False

    # Verify legacy SHA-256 hashes during migration.
    if re.fullmatch(r"[0-9a-f]{64}", hashed_password):
        legacy_hash = hashlib.sha256(
            plain_password.encode("utf-8")
        ).hexdigest()

        return hmac.compare_digest(legacy_hash, hashed_password)
            # Verify existing bcrypt hashes during migration.
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except (ValueError, TypeError):
            return False

    # Verify modern Argon2id hashes.
    try:
        if password_hasher is None:
            return False
        return password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Check whether a password hash needs upgrading."""

    if not hashed_password:
        return False
            # All existing bcrypt hashes must be upgraded to Argon2id.
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        return True

    # All legacy SHA-256 hashes must be upgraded.
    if re.fullmatch(r"[0-9a-f]{64}", hashed_password):
        return True

    try:
        if password_hasher is None:
            return False
        return password_hasher.check_needs_rehash(hashed_password)
    except (VerificationError, InvalidHashError):
        return False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""

    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.PyJWTError:
        return None
