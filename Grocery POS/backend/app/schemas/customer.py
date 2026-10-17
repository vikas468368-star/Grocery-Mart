from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CustomerBase(BaseModel):
    name: str = Field(..., example="John Doe")
    phone: Optional[str] = Field(None, example="+1234567890")
    email: Optional[str] = Field(None, example="john@example.com")

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    loyalty_points: int
    total_spent: float
    created_at: datetime

    class Config:
        from_attributes = True
