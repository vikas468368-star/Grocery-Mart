
"""Role-Based Access Control (RBAC) and JWT Authentication dependencies."""

from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole


# HTTP Bearer scheme for JWT authentication in Swagger
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate JWT access token and return the current user."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)

    if not payload:
        raise credentials_exception

    username = payload.get("sub")

    if not isinstance(username, str) or not username:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.username == username, User.is_active.is_(True))
        .first()
    )

    if not user:
        raise credentials_exception

    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Return the user if authenticated, otherwise None."""

    if not credentials:
        return None

    payload = decode_access_token(credentials.credentials)

    if not payload:
        return None

    username = payload.get("sub")

    if not isinstance(username, str) or not username:
        return None

    return (
        db.query(User)
        .filter(User.username == username, User.is_active.is_(True))
        .first()
    )


def require_roles(*allowed_roles: UserRole):
    """Create a dependency to enforce role-based access control."""

    def role_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:

        user_role_val = (
            current_user.role.value
            if hasattr(current_user.role, "value")
            else str(current_user.role)
        )

        allowed_vals = [
            role.value if hasattr(role, "value") else str(role)
            for role in allowed_roles
        ]

        if user_role_val not in allowed_vals:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Insufficient permissions.",
            )

        return current_user

    return role_dependency


# Convenience RBAC dependencies
require_owner = require_roles(UserRole.OWNER)
require_manager = require_roles(UserRole.OWNER, UserRole.MANAGER)
require_cashier = require_roles(
    UserRole.OWNER,
    UserRole.MANAGER,
    UserRole.CASHIER,
)
