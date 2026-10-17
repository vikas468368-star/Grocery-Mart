from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_owner
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["Users & Staff (Owner Only)"])

@router.get("/", response_model=List[UserResponse])
def get_users(
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """Retrieve all store users and cashiers. Restricted to Store Owner."""
    return db.query(User).filter(User.is_active == True).order_by(User.id.asc()).all()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_staff_user(
    user_in: UserCreate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """Register a new staff member (Manager or Cashier). Restricted to Store Owner."""
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username is already taken.")
    
    new_user = User(
        username=user_in.username,
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        phone=user_in.phone,
        is_active=user_in.is_active,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
