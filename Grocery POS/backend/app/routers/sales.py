from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.sale import Sale, SaleItem, SaleStatus
from app.models.payment import Payment

router = APIRouter(prefix="/sales", tags=["Sales History"])

class SaleItemSummary(BaseModel):
    id: int
    product_id: Optional[int]
    product_name: str
    barcode: Optional[str]
    quantity: float
    returned_quantity: float
    unit: str
    unit_price: float
    tax_rate: float
    line_total: float

class SaleReturnSummary(BaseModel):
    id: int
    return_number: str
    refund_amount: float
    refund_method: str
    created_at: datetime

class SaleDetailResponse(BaseModel):
    id: int
    invoice_number: str
    cashier_name: str
    customer_name: str
    customer_phone: Optional[str]
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    payment_method: str
    status: str
    created_at: datetime
    notes: Optional[str]
    items: List[SaleItemSummary]
    returns: List[SaleReturnSummary]

@router.get("/", response_model=List[SaleDetailResponse])
def get_sales_history(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve full sales history with itemized purchases, payment methods, and return status."""
    query = db.query(Sale).order_by(Sale.created_at.desc())

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (Sale.invoice_number.ilike(s)) |
            (Sale.customer_name.ilike(s)) |
            (Sale.customer_phone.ilike(s))
        )

    if status_filter:
        query = query.filter(Sale.status == status_filter)

    sales = query.offset(skip).limit(limit).all()
    results = []

    for s in sales:
        # Determine primary payment method
        pm_display = "CASH"
        if s.payments:
            pm_display = s.payments[0].payment_method.value
            if len(s.payments) > 1:
                pm_display = "SPLIT"

        cashier_disp = s.cashier.full_name if s.cashier else "Cashier #01"

        items_summary = [
            SaleItemSummary(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                barcode=item.barcode,
                quantity=item.quantity,
                returned_quantity=item.returned_quantity or 0.0,
                unit=item.unit,
                unit_price=item.unit_price,
                tax_rate=item.tax_rate,
                line_total=item.line_total,
            )
            for item in s.items
        ]

        returns_summary = [
            SaleReturnSummary(
                id=r.id,
                return_number=r.return_number,
                refund_amount=r.refund_amount,
                refund_method=r.refund_method,
                created_at=r.created_at,
            )
            for r in (s.returns or [])
        ]

        results.append(SaleDetailResponse(
            id=s.id,
            invoice_number=s.invoice_number,
            cashier_name=cashier_disp,
            customer_name=s.customer_name or "Walk-in Customer",
            customer_phone=s.customer_phone,
            subtotal=s.subtotal,
            tax_amount=s.tax_amount,
            discount_amount=s.discount_amount,
            total_amount=s.grand_total,
            payment_method=pm_display,
            status=s.status.value if hasattr(s.status, 'value') else str(s.status),
            created_at=s.created_at,
            notes=s.notes,
            items=items_summary,
            returns=returns_summary,
        ))

    return results

@router.get("/{sale_id}", response_model=SaleDetailResponse)
def get_sale_detail(sale_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific sale."""
    s = db.query(Sale).filter(Sale.id == sale_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Sale not found")

    pm_display = "CASH"
    if s.payments:
        pm_display = s.payments[0].payment_method.value
        if len(s.payments) > 1:
            pm_display = "SPLIT"

    cashier_disp = s.cashier.full_name if s.cashier else "Cashier #01"

    items_summary = [
        SaleItemSummary(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            barcode=item.barcode,
            quantity=item.quantity,
            returned_quantity=item.returned_quantity or 0.0,
            unit=item.unit,
            unit_price=item.unit_price,
            tax_rate=item.tax_rate,
            line_total=item.line_total,
        )
        for item in s.items
    ]

    returns_summary = [
        SaleReturnSummary(
            id=r.id,
            return_number=r.return_number,
            refund_amount=r.refund_amount,
            refund_method=r.refund_method,
            created_at=r.created_at,
        )
        for r in (s.returns or [])
    ]

    return SaleDetailResponse(
        id=s.id,
        invoice_number=s.invoice_number,
        cashier_name=cashier_disp,
        customer_name=s.customer_name or "Walk-in Customer",
        customer_phone=s.customer_phone,
        subtotal=s.subtotal,
        tax_amount=s.tax_amount,
        discount_amount=s.discount_amount,
        total_amount=s.grand_total,
        payment_method=pm_display,
        status=s.status.value if hasattr(s.status, 'value') else str(s.status),
        created_at=s.created_at,
        notes=s.notes,
        items=items_summary,
        returns=returns_summary,
    )
