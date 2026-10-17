from typing import List, Optional
from datetime import datetime
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.auth import require_manager
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
from app.models.product import Product
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter(tags=["Suppliers & Purchase Orders"])

# --- Schemas ---

from pydantic import BaseModel, Field, field_validator

class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, example="Metro Wholesale Agrotech")
    contact_person: Optional[str] = Field(None, example="Sunil Gupta")
    email: Optional[str] = Field(None, example="supply@metrowholesale.in")
    phone: Optional[str] = Field(None, example="+91 98111 22334")
    address: Optional[str] = Field(None, example="Yard 4, APMC Market, Vashi")
    tax_number: Optional[str] = Field(None, example="27AABCM1234F1Z1")
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Supplier name cannot be empty")
        return s

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    is_active: Optional[bool] = None

class SupplierResponse(SupplierBase):
    id: int
    created_at: Optional[datetime] = None
    product_count: Optional[int] = 0

    class Config:
        from_attributes = True

class POItemCreate(BaseModel):
    product_id: int = Field(..., gt=0, example=1)
    quantity_ordered: float = Field(..., gt=0, example=50.0)
    unit_cost: float = Field(..., ge=0, example=45.0)

class POItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity_ordered: float
    quantity_received: float
    unit_cost: float
    total_cost: float

    class Config:
        from_attributes = True

class PurchaseOrderCreate(BaseModel):
    supplier_id: int = Field(..., gt=0, example=1)
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[POItemCreate] = Field(..., min_length=1)

class PurchaseOrderUpdateStatus(BaseModel):
    status: PurchaseOrderStatus

class PurchaseOrderResponse(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    supplier_name: Optional[str] = None
    created_by_name: Optional[str] = None
    status: PurchaseOrderStatus
    total_amount: float
    order_date: datetime
    expected_delivery_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[POItemResponse] = []

    class Config:
        from_attributes = True

def _format_po(po: PurchaseOrder) -> dict:
    items_out = []
    for item in po.items:
        items_out.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name if item.product else f"Product #{item.product_id}",
            "quantity_ordered": item.quantity_ordered,
            "quantity_received": item.quantity_received,
            "unit_cost": item.unit_cost,
            "total_cost": item.total_cost,
        })
    return {
        "id": po.id,
        "po_number": po.po_number,
        "supplier_id": po.supplier_id,
        "supplier_name": po.supplier.name if po.supplier else "Unknown Supplier",
        "created_by_name": po.created_by_user.full_name if po.created_by_user else "System",
        "status": po.status,
        "total_amount": po.total_amount,
        "order_date": po.order_date,
        "expected_delivery_date": po.expected_delivery_date,
        "received_date": po.received_date,
        "notes": po.notes,
        "items": items_out,
    }

# --- Suppliers Endpoints ---

@router.get("/suppliers/", response_model=List[SupplierResponse])
def get_suppliers(db: Session = Depends(get_db)):
    """Retrieve all suppliers with active item counts."""
    suppliers = db.query(Supplier).filter(Supplier.is_active == True).order_by(Supplier.name.asc()).all()
    results = []
    for s in suppliers:
        p_count = db.query(Product).filter(Product.supplier_id == s.id, Product.is_active == True).count()
        results.append({
            "id": s.id,
            "name": s.name,
            "contact_person": s.contact_person,
            "email": s.email,
            "phone": s.phone,
            "address": s.address,
            "tax_number": s.tax_number,
            "is_active": s.is_active,
            "created_at": s.created_at,
            "product_count": p_count,
        })
    return results

@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Retrieve single supplier details."""
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    p_count = db.query(Product).filter(Product.supplier_id == s.id, Product.is_active == True).count()
    return {
        "id": s.id,
        "name": s.name,
        "contact_person": s.contact_person,
        "email": s.email,
        "phone": s.phone,
        "address": s.address,
        "tax_number": s.tax_number,
        "is_active": s.is_active,
        "created_at": s.created_at,
        "product_count": p_count,
    }

@router.post("/suppliers/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    supplier_in: SupplierCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Register a new grocery supplier/distributor. Restricted to Managers and Owners."""
    existing = db.query(Supplier).filter(Supplier.name == supplier_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Supplier '{supplier_in.name}' already registered")
    
    supplier = Supplier(**supplier_in.dict())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return {
        "id": supplier.id,
        "name": supplier.name,
        "contact_person": supplier.contact_person,
        "email": supplier.email,
        "phone": supplier.phone,
        "address": supplier.address,
        "tax_number": supplier.tax_number,
        "is_active": supplier.is_active,
        "created_at": supplier.created_at,
        "product_count": 0,
    }

@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_in: SupplierUpdate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Update supplier contact and address info. Restricted to Managers and Owners."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    update_data = supplier_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(supplier, field, val)
    
    db.commit()
    db.refresh(supplier)
    p_count = db.query(Product).filter(Product.supplier_id == supplier.id, Product.is_active == True).count()
    return {
        "id": supplier.id,
        "name": supplier.name,
        "contact_person": supplier.contact_person,
        "email": supplier.email,
        "phone": supplier.phone,
        "address": supplier.address,
        "tax_number": supplier.tax_number,
        "is_active": supplier.is_active,
        "created_at": supplier.created_at,
        "product_count": p_count,
    }

@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(
    supplier_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Soft-delete supplier. Restricted to Managers and Owners."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    supplier.is_active = False
    db.commit()
    return None

# --- Purchase Orders Endpoints ---

@router.get("/purchase-orders/", response_model=List[PurchaseOrderResponse])
def get_purchase_orders(
    skip: int = 0,
    limit: int = 50,
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Retrieve history of purchase orders for inventory procurement."""
    query = db.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.supplier),
        joinedload(PurchaseOrder.created_by_user),
        joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
    )
    if supplier_id:
        query = query.filter(PurchaseOrder.supplier_id == supplier_id)
    
    orders = query.order_by(PurchaseOrder.order_date.desc()).offset(skip).limit(limit).all()
    return [_format_po(po) for po in orders]

@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single purchase order."""
    po = db.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.supplier),
        joinedload(PurchaseOrder.created_by_user),
        joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
    ).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return _format_po(po)

@router.post("/purchase-orders/", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    po_in: PurchaseOrderCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Create a new procurement purchase order. Restricted to Managers and Owners."""
    supplier = db.query(Supplier).filter(Supplier.id == po_in.supplier_id, Supplier.is_active == True).first()
    if not supplier:
        raise HTTPException(status_code=400, detail="Invalid supplier ID")
    
    if not po_in.items:
        raise HTTPException(status_code=400, detail="Purchase order must contain at least one item")
    
    # Generate unique PO number
    token = secrets.token_hex(3).upper()
    po_number = f"PO-{token}"
    
    total_amount = 0.0
    po_items_entities = []

    for item in po_in.items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        if not prod:
            raise HTTPException(status_code=400, detail=f"Product with ID {item.product_id} not found")
        
        line_cost = item.quantity_ordered * item.unit_cost
        total_amount += line_cost
        
        po_item = PurchaseOrderItem(
            product_id=item.product_id,
            quantity_ordered=item.quantity_ordered,
            quantity_received=0.0,
            unit_cost=item.unit_cost,
            total_cost=round(line_cost, 2),
        )
        po_items_entities.append(po_item)
    
    new_po = PurchaseOrder(
        po_number=po_number,
        supplier_id=po_in.supplier_id,
        created_by_id=current_user.id,
        status=PurchaseOrderStatus.PENDING,
        total_amount=round(total_amount, 2),
        order_date=datetime.utcnow(),
        expected_delivery_date=po_in.expected_delivery_date,
        notes=po_in.notes,
        items=po_items_entities,
    )
    
    db.add(new_po)
    db.commit()
    db.refresh(new_po)
    return _format_po(new_po)

@router.put("/purchase-orders/{po_id}/status", response_model=PurchaseOrderResponse)
def update_purchase_order_status(
    po_id: int,
    status_update: PurchaseOrderUpdateStatus,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Update purchase order status. Marking as RECEIVED automatically increments product inventory stock."""
    po = db.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.supplier),
        joinedload(PurchaseOrder.created_by_user),
        joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
    ).filter(PurchaseOrder.id == po_id).first()
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    old_status = po.status
    new_status = status_update.status
    
    # If transitioning to RECEIVED for the first time, increment stock
    if new_status == PurchaseOrderStatus.RECEIVED and old_status != PurchaseOrderStatus.RECEIVED:
        po.received_date = datetime.utcnow()
        for item in po.items:
            item.quantity_received = item.quantity_ordered
            if item.product:
                item.product.stock_quantity += item.quantity_ordered
                # Optionally update cost price if new unit cost given
                if item.unit_cost > 0:
                    item.product.cost_price = item.unit_cost
    
    po.status = new_status
    db.commit()
    db.refresh(po)
    return _format_po(po)
