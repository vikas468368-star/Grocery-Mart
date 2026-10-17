from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole

class UserLogin(BaseModel):
    username: str = Field(..., example="owner")
    password: str = Field(..., example="password123")

class UserBase(BaseModel):
    username: str = Field(..., example="cashier1")
    full_name: str = Field(..., example="Rahul Sharma")
    email: Optional[str] = Field(None, example="cashier1@grocerypos.com")
    role: UserRole = Field(default=UserRole.CASHIER, example=UserRole.CASHIER)
    phone: Optional[str] = Field(None, example="+91 98200 00003")
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=4, example="password123")

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
