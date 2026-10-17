from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.sale import Sale, SaleStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.order import Order
from app.core.auth import get_optional_user
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["Payments & Receipts Engine"])

# --- Schemas ---

class SplitPaymentEntry(BaseModel):
    method: str = Field(..., description="CASH, CARD, UPI, or STORE_CREDIT")
    amount: float = Field(..., gt=0)
    tendered_amount: Optional[float] = None
    transaction_reference: Optional[str] = None

class RecordPaymentRequest(BaseModel):
    sale_id: Optional[int] = None
    invoice_number: Optional[str] = None
    payment_method: str = Field("CASH", description="CASH, CARD, UPI, or SPLIT")
    amount: float = Field(..., gt=0)
    tendered_amount: Optional[float] = None
    transaction_reference: Optional[str] = None
    split_breakdown: Optional[List[SplitPaymentEntry]] = None
    notes: Optional[str] = None

class PaymentItemResponse(BaseModel):
    id: int
    sale_id: int
    payment_method: str
    amount: float
    tendered_amount: Optional[float]
    change_amount: float
    transaction_reference: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class RecordPaymentResponse(BaseModel):
    success: bool
    message: str
    invoice_number: str
    sale_status: str
    sale_total: float
    total_paid: float
    change_amount: float
    payment_method: str
    payments: List[PaymentItemResponse]

# --- Helper ---

def parse_payment_method(name: str) -> PaymentMethod:
    name_upper = name.strip().upper()
    if name_upper in PaymentMethod.__members__:
        return PaymentMethod[name_upper]
    if name_upper in ["CREDIT_CARD", "DEBIT_CARD", "CARD"]:
        return PaymentMethod.CARD
    if name_upper in ["UPI", "QR", "GPAY", "PHONEPE", "PAYTM"]:
        return PaymentMethod.UPI
    if name_upper in ["SPLIT", "MULTI"]:
        return PaymentMethod.SPLIT
    return PaymentMethod.CASH

# --- Endpoints ---

@router.post("/record", response_model=RecordPaymentResponse, status_code=status.HTTP_201_CREATED)
def record_payment(
    payload: RecordPaymentRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Record a payment (Cash, Card, UPI, or Split) for a sale and update the Sale status to 'Paid'."""
    # Find the target Sale
    sale = None
    if payload.sale_id:
        sale = db.query(Sale).filter(Sale.id == payload.sale_id).first()
    elif payload.invoice_number:
        sale = db.query(Sale).filter(Sale.invoice_number == payload.invoice_number).first()

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale transaction not found for ID '{payload.sale_id}' or Invoice '{payload.invoice_number}'."
        )

    method_enum = parse_payment_method(payload.payment_method)
    created_payments = []
    total_paid = 0.0
    overall_change = 0.0

    if method_enum == PaymentMethod.SPLIT:
        if not payload.split_breakdown or len(payload.split_breakdown) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Split payment requires at least one split payment line in 'split_breakdown'."
            )

        split_sum = sum(item.amount for item in payload.split_breakdown)
        if round(split_sum, 2) < round(sale.grand_total, 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Total split payments (₹{round(split_sum, 2)}) do not cover the sale total (₹{sale.grand_total})."
                )
            )

        for split_item in payload.split_breakdown:
            sub_method = parse_payment_method(split_item.method)
            sub_tendered = split_item.tendered_amount or split_item.amount
            sub_change = max(0.0, sub_tendered - split_item.amount) if sub_method == PaymentMethod.CASH else 0.0
            overall_change += sub_change

            pmt = Payment(
                sale_id=sale.id,
                payment_method=sub_method,
                amount=round(split_item.amount, 2),
                tendered_amount=round(sub_tendered, 2),
                change_amount=round(sub_change, 2),
                transaction_reference=split_item.transaction_reference,
                status=PaymentStatus.PAID,
            )
            db.add(pmt)
            created_payments.append(pmt)
            total_paid += split_item.amount
    else:
        # Single payment method (CASH, CARD, UPI, STORE_CREDIT)
        tendered = payload.tendered_amount if payload.tendered_amount is not None else payload.amount
        change_due = max(0.0, tendered - payload.amount) if method_enum == PaymentMethod.CASH else 0.0
        overall_change = change_due

        pmt = Payment(
            sale_id=sale.id,
            payment_method=method_enum,
            amount=round(payload.amount, 2),
            tendered_amount=round(tendered, 2),
            change_amount=round(change_due, 2),
            transaction_reference=payload.transaction_reference,
            status=PaymentStatus.PAID,
        )
        db.add(pmt)
        created_payments.append(pmt)
        total_paid = payload.amount

    # Update Sale record status to 'Paid'
    sale.status = SaleStatus.PAID
    if payload.notes:
        sale.notes = (sale.notes + " | " + payload.notes) if sale.notes else payload.notes

    # Sync legacy Order if present
    order = db.query(Order).filter(Order.invoice_number == sale.invoice_number).first()
    if order:
        order.payment_status = "PAID"
        order.payment_method = payload.payment_method

    db.commit()

    for p in created_payments:
        db.refresh(p)
    db.refresh(sale)

    return {
        "success": True,
        "message": f"Payment of ₹{round(total_paid, 2)} successfully recorded. Sale marked as Paid.",
        "invoice_number": sale.invoice_number,
        "sale_status": sale.status.value,
        "sale_total": sale.grand_total,
        "total_paid": round(total_paid, 2),
        "change_amount": round(overall_change, 2),
        "payment_method": payload.payment_method,
        "payments": [
            {
                "id": p.id,
                "sale_id": p.sale_id,
                "payment_method": p.payment_method.value,
                "amount": p.amount,
                "tendered_amount": p.tendered_amount,
                "change_amount": p.change_amount,
                "transaction_reference": p.transaction_reference,
                "status": p.status.value,
                "created_at": p.created_at,
            }
            for p in created_payments
        ],
    }

@router.get("/", response_model=List[PaymentItemResponse])
def list_payments(limit: int = 100, db: Session = Depends(get_db)):
    """List recent payments."""
    payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(limit).all()
    return payments

@router.get("/sale/{sale_id}", response_model=List[PaymentItemResponse])
def get_sale_payments(sale_id: int, db: Session = Depends(get_db)):
    """Get all payment records associated with a specific Sale ID."""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale.payments
