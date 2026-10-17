from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class OrderItemBase(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    unit_price: float
    quantity: float = 1.0
    unit: str = "pcs"
    tax_rate: float = 0.05
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    total: float

class OrderItemCreate(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    unit_price: float
    quantity: float = 1.0
    unit: str = "pcs"
    tax_rate: float = 0.05
    discount_amount: float = 0.0

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    cashier_name: Optional[str] = "Cashier 1"
    customer_id: Optional[int] = None
    items: List[OrderItemCreate]
    payment_method: str = Field(default="CASH", example="CASH")
    discount_amount: float = Field(default=0.0, ge=0)
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    invoice_number: str
    cashier_name: str
    customer_id: Optional[int]
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    payment_method: str
    payment_status: str
    notes: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

class BillCalculationRequest(BaseModel):
    items: List[OrderItemCreate]
    discount_percent: float = 0.0
    discount_fixed: float = 0.0

class BillCalculationResponse(BaseModel):
    subtotal: float
    tax_total: float
    discount_total: float
    grand_total: float
    item_count: int
    total_quantity: float
