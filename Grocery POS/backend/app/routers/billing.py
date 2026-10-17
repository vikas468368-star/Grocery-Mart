from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import generate_invoice_number
from app.core.auth import get_optional_user
from app.models.product import Product
from app.models.sale import Sale, SaleItem, SaleStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import BillCalculationRequest, BillCalculationResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/billing", tags=["Billing & Checkout Engine"])

# --- Schemas ---

class CartLineItem(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    barcode: Optional[str] = None
    unit_price: float = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    unit: str = "pcs"
    tax_rate: float = Field(default=0.05, ge=0.0)
    discount_amount: float = Field(default=0.0, ge=0.0)

class SplitPaymentItem(BaseModel):
    method: str
    amount: float = Field(..., gt=0)
    tendered_amount: Optional[float] = None
    transaction_reference: Optional[str] = None

class GenerateBillRequest(BaseModel):
    items: List[CartLineItem] = Field(..., min_length=1)
    discount_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    discount_fixed: float = Field(default=0.0, ge=0.0)
    tax_rate_override: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    payment_method: str = "CASH"  # CASH, CARD, UPI, WALLET, SPLIT
    split_breakdown: Optional[List[SplitPaymentItem]] = None
    tendered_amount: Optional[float] = None
    cashier_name: Optional[str] = "Cashier"
    customer_id: Optional[int] = None
    customer_name: Optional[str] = "Walk-in Customer"
    customer_phone: Optional[str] = None
    notes: Optional[str] = None

class BillItemDetail(BaseModel):
    product_id: Optional[int]
    product_name: str
    barcode: Optional[str]
    quantity: float
    unit: str
    unit_price: float
    tax_rate: float
    tax_amount: float
    discount_amount: float
    line_total: float

class GeneratedBillResponse(BaseModel):
    id: int
    invoice_number: str
    cashier_name: str
    customer_name: str
    customer_phone: Optional[str]
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    tendered_amount: float
    change_amount: float
    payment_method: str
    payment_status: str
    status: str
    created_at: datetime
    items: List[BillItemDetail]
    split_breakdown: Optional[List[dict]] = None

# --- Endpoints ---

@router.post("/calculate", response_model=BillCalculationResponse)
def calculate_bill(request: BillCalculationRequest):
    """Real-time calculation engine for subtotal, configurable taxes, discounts, and item summary."""
    subtotal = 0.0
    tax_total = 0.0
    total_quantity = 0.0

    for item in request.items:
        line_sub = item.unit_price * item.quantity
        line_tax = line_sub * (item.tax_rate if item.tax_rate is not None else 0.05)
        subtotal += line_sub
        tax_total += line_tax
        total_quantity += item.quantity

    percent_discount = (subtotal * (request.discount_percent / 100.0)) if request.discount_percent > 0 else 0.0
    total_discount = percent_discount + request.discount_fixed

    grand_total = max(0.0, subtotal + tax_total - total_discount)

    return BillCalculationResponse(
        subtotal=round(subtotal, 2),
        tax_total=round(tax_total, 2),
        discount_total=round(total_discount, 2),
        grand_total=round(grand_total, 2),
        item_count=len(request.items),
        total_quantity=round(total_quantity, 2),
    )

@router.post("/generate-bill", response_model=GeneratedBillResponse, status_code=status.HTTP_201_CREATED)
@router.post("/checkout", response_model=GeneratedBillResponse, status_code=status.HTTP_201_CREATED)
def generate_bill_and_checkout(
    bill_in: GenerateBillRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Core Billing/Checkout Engine.
    1. Validates available stock for each cart item (aborts if insufficient stock exists).
    2. Computes line items, configurable taxes, and applied discounts.
    3. Decrements inventory stock.
    4. Generates a formal bill (Sale record, Payment, and synchronizes Order record).
    """
    if not bill_in.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate bill for an empty cart. Please add items."
        )

    # 1. Stock Validation Check
    product_records = {}
    for item in bill_in.items:
        if item.product_id:
            prod = db.query(Product).filter(Product.id == item.product_id).first()
            if not prod or not prod.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product '{item.product_name}' (ID: {item.product_id}) is inactive or discontinued."
                )
            # Verify sufficient inventory stock exists
            if prod.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Insufficient stock for '{prod.name}' (Barcode: {prod.barcode}). "
                        f"Available in stock: {prod.stock_quantity} {prod.unit}, "
                        f"Requested: {item.quantity} {prod.unit}."
                    )
                )
            product_records[item.product_id] = prod

    # 2. Calculation of Subtotal, Configurable Taxes, and Discounts
    subtotal = 0.0
    total_tax = 0.0
    sale_items = []
    order_items = []
    response_items = []

    for item in bill_in.items:
        prod = product_records.get(item.product_id)
        effective_tax_rate = (
            bill_in.tax_rate_override
            if bill_in.tax_rate_override is not None
            else (item.tax_rate if item.tax_rate is not None else 0.05)
        )

        line_subtotal = item.unit_price * item.quantity
        line_tax = line_subtotal * effective_tax_rate
        line_total = line_subtotal + line_tax - item.discount_amount

        subtotal += line_subtotal
        total_tax += line_tax

        # 3. Decrement Inventory Stock
        if prod:
            prod.stock_quantity = max(0.0, prod.stock_quantity - item.quantity)

        # Build SaleItem
        sale_item = SaleItem(
            product_id=item.product_id,
            product_name=item.product_name,
            barcode=item.barcode or (prod.barcode if prod else None),
            quantity=item.quantity,
            unit=item.unit,
            unit_price=item.unit_price,
            cost_price=prod.cost_price if prod else 0.0,
            tax_rate=effective_tax_rate,
            tax_amount=round(line_tax, 2),
            discount_amount=round(item.discount_amount, 2),
            line_total=round(line_total, 2),
        )
        sale_items.append(sale_item)

        # Build OrderItem for synchronization
        order_item = OrderItem(
            product_id=item.product_id,
            product_name=item.product_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            unit=item.unit,
            tax_rate=effective_tax_rate,
            tax_amount=round(line_tax, 2),
            discount_amount=round(item.discount_amount, 2),
            total=round(line_total, 2),
        )
        order_items.append(order_item)

        response_items.append({
            "product_id": item.product_id,
            "product_name": item.product_name,
            "barcode": item.barcode or (prod.barcode if prod else None),
            "quantity": item.quantity,
            "unit": item.unit,
            "unit_price": item.unit_price,
            "tax_rate": effective_tax_rate,
            "tax_amount": round(line_tax, 2),
            "discount_amount": round(item.discount_amount, 2),
            "line_total": round(line_total, 2),
        })

    # Discounts & Grand Total Calculation
    percent_discount = (subtotal * (bill_in.discount_percent / 100.0)) if bill_in.discount_percent > 0 else 0.0
    total_discount = percent_discount + bill_in.discount_fixed
    grand_total = max(0.0, subtotal + total_tax - total_discount)

    tendered = bill_in.tendered_amount if bill_in.tendered_amount is not None else grand_total
    change_due = max(0.0, tendered - grand_total)

    invoice_no = generate_invoice_number()
    cashier_display = (
        current_user.full_name
        if current_user
        else (bill_in.cashier_name or "Cashier #01")
    )

    # 4. Create Sale Record (Status: Paid)
    sale = Sale(
        invoice_number=invoice_no,
        cashier_id=current_user.id if current_user else None,
        customer_id=bill_in.customer_id,
        customer_name=bill_in.customer_name or "Walk-in Customer",
        customer_phone=bill_in.customer_phone,
        subtotal=round(subtotal, 2),
        tax_amount=round(total_tax, 2),
        discount_amount=round(total_discount, 2),
        grand_total=round(grand_total, 2),
        status=SaleStatus.PAID,
        notes=bill_in.notes,
        items=sale_items,
    )

    # 5. Create Payment Record(s) (Cash, Card, UPI, or Split)
    split_records = []
    if bill_in.payment_method.upper() == "SPLIT" and bill_in.split_breakdown:
        for split_part in bill_in.split_breakdown:
            p_method = PaymentMethod.CASH
            part_upper = split_part.method.strip().upper()
            if part_upper in PaymentMethod.__members__:
                p_method = PaymentMethod[part_upper]
            elif part_upper in ["CARD", "CREDIT_CARD", "DEBIT_CARD"]:
                p_method = PaymentMethod.CARD
            elif part_upper in ["UPI", "QR", "GPAY", "PHONEPE"]:
                p_method = PaymentMethod.UPI

            part_tendered = split_part.tendered_amount if split_part.tendered_amount is not None else split_part.amount
            part_change = max(0.0, part_tendered - split_part.amount) if p_method == PaymentMethod.CASH else 0.0

            pmt = Payment(
                payment_method=p_method,
                amount=round(split_part.amount, 2),
                tendered_amount=round(part_tendered, 2),
                change_amount=round(part_change, 2),
                transaction_reference=split_part.transaction_reference,
                status=PaymentStatus.PAID,
            )
            sale.payments.append(pmt)
            split_records.append({
                "method": pmt.payment_method.value,
                "amount": pmt.amount,
                "tendered_amount": pmt.tendered_amount,
                "change_amount": pmt.change_amount,
                "transaction_reference": pmt.transaction_reference,
            })
    else:
        method_enum = PaymentMethod.CASH
        if bill_in.payment_method in PaymentMethod.__members__:
            method_enum = PaymentMethod[bill_in.payment_method]
        elif bill_in.payment_method.upper() in ["CARD", "CREDIT_CARD", "DEBIT_CARD"]:
            method_enum = PaymentMethod.CARD
        elif bill_in.payment_method.upper() in ["UPI", "QR", "GPAY", "PAYTM"]:
            method_enum = PaymentMethod.UPI

        payment = Payment(
            payment_method=method_enum,
            amount=round(grand_total, 2),
            tendered_amount=round(tendered, 2),
            change_amount=round(change_due, 2),
            status=PaymentStatus.PAID,
        )
        sale.payments.append(payment)
        split_records.append({
            "method": payment.payment_method.value,
            "amount": payment.amount,
            "tendered_amount": payment.tendered_amount,
            "change_amount": payment.change_amount,
        })

    db.add(sale)

    # 6. Synchronize Order Record (for legacy endpoints and unified reports)
    order = Order(
        invoice_number=invoice_no,
        cashier_name=cashier_display,
        customer_id=bill_in.customer_id,
        subtotal=round(subtotal, 2),
        tax_amount=round(total_tax, 2),
        discount_amount=round(total_discount, 2),
        total_amount=round(grand_total, 2),
        payment_method=bill_in.payment_method,
        payment_status="PAID",
        notes=bill_in.notes,
        items=order_items,
    )
    db.add(order)

    db.commit()
    db.refresh(sale)

    return {
        "id": sale.id,
        "invoice_number": sale.invoice_number,
        "cashier_name": cashier_display,
        "customer_name": sale.customer_name,
        "customer_phone": sale.customer_phone,
        "subtotal": sale.subtotal,
        "tax_amount": sale.tax_amount,
        "discount_amount": sale.discount_amount,
        "total_amount": sale.grand_total,
        "tendered_amount": round(tendered, 2),
        "change_amount": round(change_due, 2),
        "payment_method": bill_in.payment_method,
        "payment_status": "PAID",
        "status": "Paid",
        "created_at": sale.created_at,
        "items": response_items,
        "split_breakdown": split_records,
    }
