from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.auth import get_current_user
from app.models.user import User, UserRole
from app.schemas.user import UserLogin, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate store staff with username and password, returns JWT token."""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact store owner.",
        )
    
    role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "role": role_str,
        "full_name": user.full_name,
    }
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }

@router.get("/me")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve details and RBAC capabilities of the currently authenticated staff member."""
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    is_owner = role_val == UserRole.OWNER.value
    is_manager = role_val in [UserRole.OWNER.value, UserRole.MANAGER.value]
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": role_val,
        "phone": current_user.phone,
        "is_active": current_user.is_active,
        "permissions": {
            "can_view_reports": is_owner,
            "can_manage_settings": is_owner,
            "can_manage_users": is_owner,
            "can_manage_inventory": is_manager,
            "can_manage_purchases": is_manager,
            "can_bill": True,
        }
    }

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Acknowledge staff session logout."""
    return {"message": f"User {current_user.username} logged out successfully."}
