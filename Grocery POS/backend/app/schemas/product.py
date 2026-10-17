from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, example="Organic Whole Milk 1L")
    barcode: str = Field(..., min_length=1, example="890100000001")
    sku: Optional[str] = Field(None, example="DAI-001")
    category_id: Optional[int] = Field(default=1, example=1)
    supplier_id: Optional[int] = Field(default=None, example=1)
    description: Optional[str] = None
    price: float = Field(..., gt=0, example=65.00)
    cost_price: float = Field(default=0.0, ge=0, example=48.00)
    stock_quantity: float = Field(default=0.0, ge=0, example=50.0)
    min_stock_alert: float = Field(default=10.0, ge=0, example=10.0)
    unit: str = Field(default="pcs", example="pcs")
    tax_rate: float = Field(default=0.05, ge=0, le=1.0, example=0.05)
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Product name cannot be empty or whitespace only")
        return stripped

    @field_validator("barcode")
    @classmethod
    def validate_barcode(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Barcode cannot be empty or whitespace only")
        return stripped

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    stock_quantity: Optional[float] = None
    min_stock_alert: Optional[float] = None
    unit: Optional[str] = None
    tax_rate: Optional[float] = None
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    category_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
