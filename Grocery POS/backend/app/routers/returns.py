from typing import List, Optional
from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.sale import Sale, SaleItem, SaleStatus, SaleReturn, ReturnItem
from app.models.product import Product
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.order import Order
from app.core.auth import get_optional_user
from app.models.user import User

router = APIRouter(prefix="/returns", tags=["Returns & Refunds"])

# --- Schemas ---

class ReturnItemRequest(BaseModel):
    sale_item_id: Optional[int] = None
    product_id: int
    quantity: float = Field(..., gt=0)
    reason: str = "Customer Return"

class ProcessReturnRequest(BaseModel):
    sale_id: Optional[int] = None
    invoice_number: Optional[str] = None
    items: List[ReturnItemRequest] = Field(..., min_length=1)
    refund_method: str = "CASH"  # CASH, CARD, UPI, STORE_CREDIT
    notes: Optional[str] = None

class ReturnedItemDetail(BaseModel):
    product_id: int
    product_name: str
    quantity_returned: float
    unit: str
    refund_amount: float
    reason: str
    restocked: bool

class ProcessReturnResponse(BaseModel):
    success: bool
    message: str
    return_number: str
    invoice_number: str
    sale_id: int
    refund_amount: float
    refund_method: str
    sale_status: str
    returned_items: List[ReturnedItemDetail]
    created_at: datetime

class ReturnHistoryResponse(BaseModel):
    id: int
    return_number: str
    sale_id: int
    invoice_number: str
    refund_amount: float
    refund_method: str
    reason: Optional[str]
    notes: Optional[str]
    created_at: datetime
    items_count: int

# --- Helper ---

def generate_return_number() -> str:
    return f"RET-{uuid.uuid4().hex[:6].upper()}"

def parse_payment_method(name: str) -> PaymentMethod:
    name_upper = name.strip().upper()
    if name_upper in PaymentMethod.__members__:
        return PaymentMethod[name_upper]
    if name_upper in ["CARD", "CREDIT_CARD", "DEBIT_CARD"]:
        return PaymentMethod.CARD
    if name_upper in ["UPI", "QR", "GPAY", "PHONEPE"]:
        return PaymentMethod.UPI
    return PaymentMethod.CASH

# --- Endpoints ---

@router.post("/process", response_model=ProcessReturnResponse, status_code=status.HTTP_201_CREATED)
def process_return_and_refund(
    payload: ProcessReturnRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Process customer returns & refunds.
    1. Validates purchased items and available returnable quantities.
    2. Automatically adds stock back into the Product table.
    3. Reverses the payment (creates negative/refund payment ledger record).
    4. Updates the Sale record status to 'REFUNDED' (or partial refund).
    5. Generates formal SaleReturn & ReturnItem records.
    """
    if not payload.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot process return without any selected items."
        )

    # 1. Lookup Sale
    sale = None
    if payload.sale_id:
        sale = db.query(Sale).filter(Sale.id == payload.sale_id).first()
    elif payload.invoice_number:
        sale = db.query(Sale).filter(Sale.invoice_number == payload.invoice_number).first()

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale not found for ID '{payload.sale_id}' or Invoice '{payload.invoice_number}'."
        )

    if sale.status == SaleStatus.REFUNDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sale '{sale.invoice_number}' has already been fully refunded."
        )

    return_no = generate_return_number()
    total_refund = 0.0
    return_items_entities = []
    returned_details = []

    # 2. Process each item return
    for ret_item in payload.items:
        # Match with SaleItem
        sale_item = next(
            (si for si in sale.items if (ret_item.sale_item_id and si.id == ret_item.sale_item_id) or si.product_id == ret_item.product_id),
            None
        )

        if not sale_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product ID {ret_item.product_id} was not part of sale invoice '{sale.invoice_number}'."
            )

        already_returned = sale_item.returned_quantity or 0.0
        remaining_returnable = sale_item.quantity - already_returned

        if round(ret_item.quantity, 2) > round(remaining_returnable, 2) + 0.001:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot return {ret_item.quantity} {sale_item.unit} of '{sale_item.product_name}'. "
                    f"Only {remaining_returnable} {sale_item.unit} remain returnable from original purchase of {sale_item.quantity} {sale_item.unit}."
                )
            )

        # Proportional refund computation
        unit_effective_price = sale_item.line_total / sale_item.quantity
        line_refund = round(unit_effective_price * ret_item.quantity, 2)
        total_refund += line_refund

        # Update returned quantity on sale item
        sale_item.returned_quantity = round(already_returned + ret_item.quantity, 2)

        # Restock inventory stock back into Product table
        prod = db.query(Product).filter(Product.id == sale_item.product_id).first()
        restocked_ok = False
        if prod:
            prod.stock_quantity = round(prod.stock_quantity + ret_item.quantity, 2)
            restocked_ok = True

        # Build ReturnItem entity
        ritem = ReturnItem(
            sale_item_id=sale_item.id,
            product_id=sale_item.product_id,
            product_name=sale_item.product_name,
            quantity=ret_item.quantity,
            unit=sale_item.unit,
            refund_unit_price=round(unit_effective_price, 2),
            refund_subtotal=line_refund,
            reason=ret_item.reason,
        )
        return_items_entities.append(ritem)

        returned_details.append({
            "product_id": sale_item.product_id,
            "product_name": sale_item.product_name,
            "quantity_returned": ret_item.quantity,
            "unit": sale_item.unit,
            "refund_amount": line_refund,
            "reason": ret_item.reason,
            "restocked": restocked_ok,
        })

    # 3. Create SaleReturn Record
    sale_return = SaleReturn(
        return_number=return_no,
        sale_id=sale.id,
        refund_amount=round(total_refund, 2),
        refund_method=payload.refund_method,
        reason=payload.notes or "Customer Return / Refund",
        notes=payload.notes,
        items=return_items_entities,
    )
    db.add(sale_return)

    # 4. Reverse the Payment
    pmt_enum = parse_payment_method(payload.refund_method)
    refund_payment = Payment(
        sale_id=sale.id,
        payment_method=pmt_enum,
        amount=-round(total_refund, 2),
        tendered_amount=round(total_refund, 2),
        change_amount=0.0,
        transaction_reference=f"REFUND-{return_no}",
        status=PaymentStatus.REFUNDED,
    )
    sale.payments.append(refund_payment)

    # 5. Check if all items are fully returned
    all_returned = all(
        round(si.returned_quantity or 0.0, 2) >= round(si.quantity, 2) - 0.001
        for si in sale.items
    )

    if all_returned:
        sale.status = SaleStatus.REFUNDED
    else:
        # Partial refund status
        sale.notes = (sale.notes or "") + f" | Partial Return {return_no} (₹{round(total_refund, 2)})"

    # Synchronize legacy Order if present
    order = db.query(Order).filter(Order.invoice_number == sale.invoice_number).first()
    if order and all_returned:
        order.payment_status = "REFUNDED"

    db.commit()
    db.refresh(sale)
    db.refresh(sale_return)

    return {
        "success": True,
        "message": f"Successfully processed return {return_no}. Refunded ₹{round(total_refund, 2)} and added items back to inventory stock.",
        "return_number": return_no,
        "invoice_number": sale.invoice_number,
        "sale_id": sale.id,
        "refund_amount": round(total_refund, 2),
        "refund_method": payload.refund_method,
        "sale_status": sale.status.value,
        "returned_items": returned_details,
        "created_at": sale_return.created_at,
    }

@router.get("/", response_model=List[ReturnHistoryResponse])
def get_all_returns(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve history of all processed customer returns and refunds."""
    returns = db.query(SaleReturn).order_by(SaleReturn.created_at.desc()).limit(limit).all()
    results = []
    for ret in returns:
        results.append({
            "id": ret.id,
            "return_number": ret.return_number,
            "sale_id": ret.sale_id,
            "invoice_number": ret.sale.invoice_number if ret.sale else f"SALE-{ret.sale_id}",
            "refund_amount": ret.refund_amount,
            "refund_method": ret.refund_method,
            "reason": ret.reason,
            "notes": ret.notes,
            "created_at": ret.created_at,
            "items_count": len(ret.items),
        })
    return results

@router.get("/sale/{sale_id}", response_model=List[ReturnHistoryResponse])
def get_returns_for_sale(sale_id: int, db: Session = Depends(get_db)):
    """Get returns associated with a specific sale."""
    returns = db.query(SaleReturn).filter(SaleReturn.sale_id == sale_id).order_by(SaleReturn.created_at.desc()).all()
    results = []
    for ret in returns:
        results.append({
            "id": ret.id,
            "return_number": ret.return_number,
            "sale_id": ret.sale_id,
            "invoice_number": ret.sale.invoice_number if ret.sale else f"SALE-{ret.sale_id}",
            "refund_amount": ret.refund_amount,
            "refund_method": ret.refund_method,
            "reason": ret.reason,
            "notes": ret.notes,
            "created_at": ret.created_at,
            "items_count": len(ret.items),
        })
    return results
