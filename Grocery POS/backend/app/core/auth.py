"""Role-Based Access Control (RBAC) and Authentication dependencies."""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole

# OAuth2 password bearer scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Validate JWT access token and return current User."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if not username:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        raise credentials_exception
    
    return user

def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Return user if authenticated, or None if guest."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    username = payload.get("sub")
    if not username:
        return None
    return db.query(User).filter(User.username == username, User.is_active == True).first()

def require_roles(*allowed_roles: UserRole):
    """Factory creating dependency to enforce Role-Based Access Control (RBAC)."""
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        # Check enum match
        user_role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        allowed_vals = [r.value if hasattr(r, 'value') else str(r) for r in allowed_roles]
        
        if user_role_val not in allowed_vals:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of: {allowed_vals}. Current role: '{user_role_val}'.",
            )
        return current_user
    return role_dependency

# Convenience RBAC dependencies
require_owner = require_roles(UserRole.OWNER)
require_manager = require_roles(UserRole.OWNER, UserRole.MANAGER)
require_cashier = require_roles(UserRole.OWNER, UserRole.MANAGER, UserRole.CASHIER)
